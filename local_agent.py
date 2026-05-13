#!/usr/bin/env python3
"""
Local Agent for GSH Pipeline - Hybrid AWS Deployment
Polls AWS SQS for pending jobs, executes Docker container against local genome files,
and reports completion status to CloudWatch.

Report Section: 2. Conceptual Design - Local Agent
Component: Lightweight Python service running on campus server
"""

import json
import time
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import boto3
import docker
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GSHLocalAgent')


class LocalAgent:
    """
    Local Agent for GSH Pipeline.
    
    Responsibilities:
    1. Authenticate with AWS using campus credentials
    2. Poll SQS queue for pending jobs (30-second interval)
    3. Pull Docker image from ECR if not cached locally
    4. Execute pipeline container against local genome files
    5. Upload metadata to CloudWatch
    6. Log all operations for audit trail
    """
    
    def __init__(self, config_path: str):
        """Initialize local agent from configuration file."""
        self.config = self._load_config(config_path)
        self.sqs_client = boto3.client(
            'sqs',
            region_name=self.config['aws_region']
        )
        self.cloudwatch_client = boto3.client(
            'cloudwatch',
            region_name=self.config['aws_region']
        )
        self.docker_client = docker.from_env()
        self.queue_url = self.config['sqs_queue_url']
        self.ecr_registry = self.config['ecr_registry_uri']
        self.local_data_path = Path(self.config['local_genome_path'])
        self.output_path = Path(self.config['output_path'])
        
        logger.info("Local Agent initialized successfully")
        logger.info(f"Connected to SQS queue: {self.queue_url}")
        logger.info(f"ECR Registry: {self.ecr_registry}")
        logger.info(f"Local genome path: {self.local_data_path}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_path}")
            sys.exit(1)
    
    def authenticate(self) -> bool:
        """Authenticate with AWS and verify credentials."""
        try:
            sts = boto3.client('sts', region_name=self.config['aws_region'])
            identity = sts.get_caller_identity()
            logger.info(f"Authenticated as: {identity['Arn']}")
            return True
        except ClientError as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def poll_sqs(self) -> Optional[Dict]:
        """Poll SQS queue for pending jobs. Returns None if no messages."""
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10,
                VisibilityTimeout=3600  # 1 hour timeout for job execution
            )
            
            if 'Messages' not in response:
                return None
            
            message = response['Messages'][0]
            job = json.loads(message['Body'])
            job['receipt_handle'] = message['ReceiptHandle']
            
            logger.info(f"Received job: {job['job_id']}")
            return job
        
        except ClientError as e:
            logger.error(f"Error polling SQS: {e}")
            return None
    
    def pull_docker_image(self, image_uri: str) -> bool:
        """Pull Docker image from ECR if not cached locally."""
        try:
            logger.info(f"Checking Docker image: {image_uri}")
            
            # Check if image exists locally
            try:
                self.docker_client.images.get(image_uri)
                logger.info(f"Docker image already cached: {image_uri}")
                return True
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling Docker image from ECR: {image_uri}")
                self.docker_client.images.pull(image_uri)
                logger.info(f"Successfully pulled image: {image_uri}")
                return True
        
        except Exception as e:
            logger.error(f"Error pulling Docker image: {e}")
            return False
    
    def execute_pipeline(self, job: Dict) -> bool:
        """Execute GSH pipeline in Docker container against local genome."""
        try:
            image_uri = f"{self.ecr_registry}:latest"
            
            # Prepare Docker run parameters
            volumes = {
                str(self.local_data_path): {'bind': '/data/input', 'mode': 'ro'},
                str(self.output_path): {'bind': '/data/output', 'mode': 'rw'}
            }
            
            # Extract job parameters
            params = job.get('parameters', {})
            env_vars = {
                'JOB_ID': job['job_id'],
                'RESEARCHER_ID': job['researcher_id'],
                'GENOME_PATH': job['genome_path'],
                'DIST_FROM_GENES': str(params.get('dist_from_genes', 50000)),
                'INCLUDE_ENHANCERS': str(params.get('include_enhancers', True)),
                'INCLUDE_MIRNAS': str(params.get('include_mirnas', True))
            }
            
            logger.info(f"Executing pipeline for job {job['job_id']}")
            start_time = time.time()
            
            # Run container
            container = self.docker_client.containers.run(
                image_uri,
                volumes=volumes,
                environment=env_vars,
                detach=True,
                remove=False
            )
            
            # Wait for container to complete
            exit_code = container.wait()
            logs = container.logs(decode=True)
            
            elapsed_time = time.time() - start_time
            
            logger.info(f"Pipeline execution completed for job {job['job_id']}")
            logger.info(f"Exit code: {exit_code['StatusCode']}, Runtime: {elapsed_time:.2f}s")
            
            if exit_code['StatusCode'] == 0:
                logger.info(f"Job {job['job_id']} completed successfully")
                return True
            else:
                logger.error(f"Job {job['job_id']} failed with exit code {exit_code['StatusCode']}")
                logger.error(f"Container logs: {logs}")
                return False
        
        except Exception as e:
            logger.error(f"Error executing pipeline: {e}")
            return False
    
    def upload_metadata_to_cloudwatch(self, job: Dict, status: str, runtime: float):
        """Upload job completion metadata to CloudWatch."""
        try:
            # List output files
            output_files = []
            if self.output_path.exists():
                for file in self.output_path.glob('*'):
                    if file.is_file():
                        output_files.append({
                            'name': file.name,
                            'size_bytes': file.stat().st_size
                        })
            
            # Create metric data
            namespace = 'GSH/Pipeline'
            metric_data = [
                {
                    'MetricName': 'JobCompletion',
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'Status', 'Value': status},
                        {'Name': 'Institution', 'Value': job.get('institution', 'unknown')}
                    ]
                },
                {
                    'MetricName': 'ExecutionTime',
                    'Value': runtime,
                    'Unit': 'Seconds',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {'Name': 'JobId', 'Value': job['job_id']}
                    ]
                }
            ]
            
            self.cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=metric_data
            )
            
            # Log to CloudWatch Logs as well
            logger.info(
                f"Uploaded metadata: job_id={job['job_id']}, "
                f"status={status}, runtime={runtime:.2f}s, "
                f"output_files={len(output_files)}"
            )
            return True
        
        except ClientError as e:
            logger.error(f"Error uploading metadata to CloudWatch: {e}")
            return False
    
    def delete_job_from_queue(self, receipt_handle: str) -> bool:
        """Remove processed job from SQS queue."""
        try:
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info("Job removed from queue")
            return True
        except ClientError as e:
            logger.error(f"Error deleting job from queue: {e}")
            return False
    
    def run(self, poll_interval: int = 30):
        """
        Main polling loop. Runs indefinitely, polling SQS at regular intervals.
        
        Args:
            poll_interval: Seconds between SQS polls (default: 30 as per report)
        """
        logger.info(f"Starting main polling loop (interval: {poll_interval}s)")
        
        if not self.authenticate():
            logger.error("Failed to authenticate with AWS")
            sys.exit(1)
        
        try:
            while True:
                logger.debug("Polling SQS queue...")
                job = self.poll_sqs()
                
                if job is None:
                    logger.debug("No jobs in queue")
                    time.sleep(poll_interval)
                    continue
                
                # Pull Docker image
                image_uri = f"{self.ecr_registry}:latest"
                if not self.pull_docker_image(image_uri):
                    logger.error(f"Failed to pull Docker image for job {job['job_id']}")
                    self.delete_job_from_queue(job['receipt_handle'])
                    continue
                
                # Execute pipeline
                start_time = time.time()
                success = self.execute_pipeline(job)
                runtime = time.time() - start_time
                
                # Upload metadata
                status = 'SUCCESS' if success else 'FAILED'
                self.upload_metadata_to_cloudwatch(job, status, runtime)
                
                # Remove from queue
                self.delete_job_from_queue(job['receipt_handle'])
        
        except KeyboardInterrupt:
            logger.info("Shutting down local agent")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in polling loop: {e}")
            sys.exit(1)


def main():
    """Entry point for local agent."""
    config_path = os.environ.get('GSH_CONFIG_PATH', './config.json')
    agent = LocalAgent(config_path)
    agent.run()


if __name__ == '__main__':
    main()
