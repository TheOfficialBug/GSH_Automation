#!/usr/bin/env python3
"""
CLI Tool: gsh-status
Check the status of a submitted GSH Pipeline job.

Report Section: 4. User Guide - Command-line Interface
Usage: gsh-status <job-id> [--profile <aws_profile>]

Example:
  gsh-status a1b2c3d4-e5f6-7890-abcd-ef1234567890
"""

import argparse
import json
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta


def main():
    """Main entry point for gsh-status CLI."""
    parser = argparse.ArgumentParser(
        description='Check the status of a GSH Pipeline job'
    )
    
    parser.add_argument(
        'job_id',
        help='Job ID (UUID format)'
    )
    
    parser.add_argument(
        '--profile', '-p',
        help='AWS profile to use (uses default profile if not specified)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='~/.gsh/config.json',
        help='Path to GSH configuration file'
    )
    
    parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='Show detailed job information'
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Watch job status (updates every 5 seconds)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_path = Path(args.config).expanduser()
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Get AWS credentials
        session = boto3.Session(profile_name=args.profile)
        
        if args.watch:
            watch_job_status(session, args.job_id, config, args.detailed)
        else:
            status = get_job_status(session, args.job_id, config)
            display_job_status(status, args.detailed)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_job_status(session: boto3.Session, job_id: str, config: dict) -> dict:
    """Retrieve job status from AWS."""
    try:
        cloudwatch = session.client('cloudwatch', region_name=config.get('aws_region', 'us-east-1'))
        sqs = session.client('sqs', region_name=config.get('aws_region', 'us-east-1'))
        
        # Query CloudWatch for job metrics
        response = cloudwatch.get_metric_statistics(
            Namespace='GSH/Pipeline',
            MetricName='JobCompletion',
            Dimensions=[{'Name': 'JobId', 'Value': job_id}],
            StartTime=get_utc_time_minus(hours=24),
            EndTime=get_utc_time(),
            Period=3600,
            Statistics=['Sum', 'Maximum']
        )
        
        # Query execution time metric
        runtime_response = cloudwatch.get_metric_statistics(
            Namespace='GSH/Pipeline',
            MetricName='ExecutionTime',
            Dimensions=[{'Name': 'JobId', 'Value': job_id}],
            StartTime=get_utc_time_minus(hours=24),
            EndTime=get_utc_time(),
            Period=60,
            Statistics=['Average']
        )
        
        # Determine status
        if response['Datapoints']:
            status = 'COMPLETED'
            runtime = runtime_response['Datapoints'][0]['Average'] if runtime_response['Datapoints'] else 0
        else:
            status = 'PENDING'
            runtime = 0
        
        return {
            'job_id': job_id,
            'status': status,
            'runtime_seconds': int(runtime),
            'last_updated': datetime.utcnow().isoformat(),
            'queue_depth': get_queue_depth(sqs, config)
        }
    
    except Exception as e:
        return {
            'job_id': job_id,
            'status': 'UNKNOWN',
            'error': str(e)
        }


def get_queue_depth(sqs, config: dict) -> int:
    """Get number of jobs in queue."""
    try:
        queue_url = config.get('sqs_queue_url')
        if queue_url:
            response = sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['ApproximateNumberOfMessages']
            )
            return int(response['Attributes']['ApproximateNumberOfMessages'])
    except:
        pass
    return 0


def display_job_status(status: dict, detailed: bool = False):
    """Display job status to console."""
    job_id = status['job_id']
    current_status = status['status']
    
    status_symbol = "⏳" if current_status == "PENDING" else "✅" if current_status == "COMPLETED" else "❓"
    
    print(f"\n{status_symbol} Job Status")
    print("=" * 50)
    print(f"Job ID:        {job_id}")
    print(f"Status:        {current_status}")
    
    if current_status == 'COMPLETED':
        runtime = status.get('runtime_seconds', 0)
        minutes = runtime // 60
        seconds = runtime % 60
        print(f"Runtime:       {minutes}m {seconds}s")
    else:
        queue_depth = status.get('queue_depth', 0)
        if queue_depth > 0:
            print(f"Queue Position: ~{queue_depth} job(s) ahead")
    
    print(f"Last Updated:  {status.get('last_updated', 'N/A')}")
    
    if 'error' in status:
        print(f"Error:         {status['error']}")
    
    if detailed:
        print("\nDetailed Information:")
        print(f"  Runtime: {status.get('runtime_seconds', 0)} seconds")
        print(f"  Queue Depth: {status.get('queue_depth', 0)} jobs")
    
    print()


def watch_job_status(session: boto3.Session, job_id: str, config: dict, detailed: bool = False):
    """Watch job status with updates every 5 seconds."""
    import time
    
    print(f"Watching job {job_id}...")
    print("Press Ctrl+C to stop watching\n")
    
    try:
        while True:
            status = get_job_status(session, job_id, config)
            
            # Clear screen (works on Unix-like systems)
            print("\033[2J\033[H", end="")
            
            display_job_status(status, detailed)
            
            if status['status'] == 'COMPLETED':
                print("Job completed! Watch mode stopped.")
                break
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nWatch mode stopped.")


def get_utc_time():
    """Get current UTC time."""
    return datetime.utcnow()


def get_utc_time_minus(minutes: int = 0, hours: int = 0, days: int = 0):
    """Get UTC time minus specified duration."""
    return datetime.utcnow() - timedelta(minutes=minutes, hours=hours, days=days)


if __name__ == '__main__':
    main()
