#!/usr/bin/env python3
"""
CLI Tool: gsh-submit
Submit a new GSH Pipeline job for analysis.

Report Section: 4. User Guide - Command-line Interface
Usage: gsh-submit --genome <path> [--dist-genes <int>] [--enhancers] [--mirnas]

Example:
  gsh-submit --genome /data/genomes/danio_rerio.bed --dist-genes 50000 --enhancers --mirnas
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict
import boto3
from botocore.exceptions import ClientError


def main():
    """Main entry point for gsh-submit CLI."""
    parser = argparse.ArgumentParser(
        description='Submit a GSH Pipeline job for analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic submission with default parameters
  gsh-submit --genome /data/genomes/danio_rerio.bed
  
  # Advanced submission with custom parameters
  gsh-submit --genome /data/genomes/danio_rerio.bed \\
    --dist-genes 75000 --enhancers --mirnas --researcher-id researcher@penn.edu
"""
    )
    
    parser.add_argument(
        '--genome', '-g',
        required=True,
        help='Path to genome BED file (local path, must be accessible to local agent)'
    )
    
    parser.add_argument(
        '--dist-genes', '-d',
        type=int,
        default=50000,
        help='Minimum distance from genes in base pairs (default: 50000)'
    )
    
    parser.add_argument(
        '--enhancers', '-e',
        action='store_true',
        default=True,
        help='Include enhancer regions in filtering (default: True)'
    )
    
    parser.add_argument(
        '--mirnas', '-m',
        action='store_true',
        default=True,
        help='Include miRNA sites in filtering (default: True)'
    )
    
    parser.add_argument(
        '--researcher-id', '-r',
        help='Researcher identifier (auto-detected from AWS credentials if not provided)'
    )
    
    parser.add_argument(
        '--institution', '-i',
        help='Institution code (auto-detected from AWS context if not provided)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='~/.gsh/config.json',
        help='Path to GSH configuration file (default: ~/.gsh/config.json)'
    )
    
    parser.add_argument(
        '--profile', '-p',
        help='AWS profile to use (uses default profile if not specified)'
    )
    
    parser.add_argument(
        '--wait', '-w',
        action='store_true',
        help='Wait for job completion (polls every 30 seconds)'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate genome file exists
        genome_path = Path(args.genome).expanduser()
        if not genome_path.exists():
            print(f"Error: Genome file not found: {args.genome}", file=sys.stderr)
            sys.exit(1)
        
        # Load configuration
        config_path = Path(args.config).expanduser()
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Get AWS credentials
        session = boto3.Session(profile_name=args.profile)
        lambda_client = session.client('lambda', region_name=config.get('aws_region', 'us-east-1'))
        
        # Prepare job submission
        researcher_id = args.researcher_id or get_researcher_id_from_aws(session)
        institution = args.institution or get_institution_from_aws(session, config)
        
        job_payload = {
            'researcher_id': researcher_id,
            'institution': institution,
            'genome_path': str(genome_path),
            'parameters': {
                'dist_from_genes': args.dist_genes,
                'include_enhancers': args.enhancers,
                'include_mirnas': args.mirnas
            }
        }
        
        print(f"Submitting job for {researcher_id} at {institution}...")
        print(f"Genome: {args.genome}")
        print(f"Parameters: dist_from_genes={args.dist_genes}, enhancers={args.enhancers}, mirnas={args.mirnas}")
        
        # Invoke Lambda function
        lambda_function = config.get('job_validator_lambda', 'gsh-job-validator')
        response = lambda_client.invoke(
            FunctionName=lambda_function,
            InvocationType='RequestResponse',
            Payload=json.dumps(job_payload)
        )
        
        # Parse response
        payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            result = json.loads(payload.get('body', '{}'))
            job_id = result.get('job_id')
            print(f"\n✅ Job submitted successfully!")
            print(f"Job ID: {job_id}")
            print(f"Status: {result.get('status')}")
            print(f"Estimated wait time: {result.get('estimated_wait_time_minutes', 5)} minutes")
            
            if args.wait:
                print("\nWaiting for job completion...")
                wait_for_job(session, job_id, config)
        else:
            error = json.loads(payload.get('body', '{}'))
            print(f"❌ Submission failed: {error.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_researcher_id_from_aws(session: boto3.Session) -> str:
    """Extract researcher ID from AWS identity."""
    try:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        arn = identity['Arn']
        # Extract username from ARN (format: arn:aws:iam::ACCOUNT:user/username)
        return arn.split('/')[-1]
    except Exception as e:
        print(f"Warning: Could not determine researcher ID from AWS: {e}", file=sys.stderr)
        return input("Enter your researcher ID: ").strip()


def get_institution_from_aws(session: boto3.Session, config: Dict) -> str:
    """Determine institution from AWS context."""
    try:
        ec2 = session.client('ec2')
        vpcs = ec2.describe_vpcs()['Vpcs']
        
        # Try to match VPC to institution based on config
        for vpc in vpcs:
            for institution, details in config.get('institutions', {}).items():
                if vpc.get('CidrBlock') == details.get('vpn_subnet'):
                    return institution
        
        # Fall back to user input
        print("Available institutions:", ', '.join(config.get('institutions', {}).keys()))
        return input("Enter your institution: ").strip().lower()
    except Exception:
        print("Available institutions:", ', '.join(config.get('institutions', {}).keys()))
        return input("Enter your institution: ").strip().lower()


def wait_for_job(session: boto3.Session, job_id: str, config: Dict):
    """Poll for job completion."""
    import time
    
    cloudwatch = session.client('cloudwatch', region_name=config.get('aws_region', 'us-east-1'))
    
    while True:
        try:
            # Query CloudWatch for job status
            response = cloudwatch.get_metric_statistics(
                Namespace='GSH/Pipeline',
                MetricName='JobCompletion',
                Dimensions=[{'Name': 'JobId', 'Value': job_id}],
                StartTime=get_utc_time_minus(minutes=5),
                EndTime=get_utc_time(),
                Period=60,
                Statistics=['Sum']
            )
            
            if response['Datapoints']:
                print(f"✅ Job {job_id} completed!")
                break
            
            print(".", end="", flush=True)
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nJob submission stopped, but will continue running on AWS.")
            break
        except Exception as e:
            print(f"\nWarning: Could not poll job status: {e}", file=sys.stderr)
            break


def get_utc_time():
    """Get current UTC time."""
    from datetime import datetime
    return datetime.utcnow()


def get_utc_time_minus(minutes: int = 0, hours: int = 0):
    """Get UTC time minus specified duration."""
    from datetime import datetime, timedelta
    return datetime.utcnow() - timedelta(minutes=minutes, hours=hours)


if __name__ == '__main__':
    main()
