#!/usr/bin/env python3
"""
CLI Tool: gsh-logs
Retrieve logs for a GSH Pipeline job.

Report Section: 4. User Guide - Command-line Interface
Usage: gsh-logs <job-id> [--lines <num>] [--since <time>]

Example:
  gsh-logs a1b2c3d4-e5f6-7890-abcd-ef1234567890 --lines 50
  gsh-logs a1b2c3d4-e5f6-7890-abcd-ef1234567890 --since 10m
"""

import argparse
import json
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import re


def main():
    """Main entry point for gsh-logs CLI."""
    parser = argparse.ArgumentParser(
        description='Retrieve logs for a GSH Pipeline job'
    )
    
    parser.add_argument(
        'job_id',
        help='Job ID (UUID format)'
    )
    
    parser.add_argument(
        '--lines', '-n',
        type=int,
        default=100,
        help='Number of log lines to retrieve (default: 100)'
    )
    
    parser.add_argument(
        '--since', '-s',
        help='Retrieve logs from specified time (e.g., 10m, 1h, 30s)'
    )
    
    parser.add_argument(
        '--filter', '-f',
        help='Filter logs by keyword (case-insensitive)'
    )
    
    parser.add_argument(
        '--level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Filter logs by level'
    )
    
    parser.add_argument(
        '--profile', '-p',
        help='AWS profile to use'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='~/.gsh/config.json',
        help='Path to GSH configuration file'
    )
    
    parser.add_argument(
        '--follow', '-f',
        action='store_true',
        dest='follow_logs',
        help='Follow logs in real-time (like tail -f)'
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
        
        # Parse time range
        start_time = parse_time_offset(args.since) if args.since else get_utc_time_minus(hours=24)
        
        # Retrieve logs
        logs = retrieve_logs(
            session, args.job_id, config,
            start_time=start_time,
            max_lines=args.lines,
            filter_keyword=args.filter,
            filter_level=args.level
        )
        
        # Display logs
        display_logs(logs, args.job_id)
        
        if args.follow_logs:
            follow_logs(session, args.job_id, config, start_time)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def retrieve_logs(session: boto3.Session, job_id: str, config: dict,
                  start_time: datetime = None, max_lines: int = 100,
                  filter_keyword: str = None, filter_level: str = None) -> list:
    """Retrieve logs from CloudWatch."""
    try:
        logs_client = session.client('logs', region_name=config.get('aws_region', 'us-east-1'))
        
        log_group = f"/aws/lambda/gsh-job-{job_id}"
        
        try:
            # Query CloudWatch Logs
            query = f"fields @timestamp, @message, @logStream | filter @message like /.*/"
            
            if filter_keyword:
                query += f" and @message like /{filter_keyword}/"
            
            if filter_level:
                query += f' and @message like /{filter_level}/'
            
            query += " | sort @timestamp desc | limit " + str(max_lines)
            
            response = logs_client.start_query(
                logGroupName=log_group,
                startTime=int(start_time.timestamp()),
                endTime=int(get_utc_time().timestamp()),
                queryString=query
            )
            
            query_id = response['queryId']
            
            # Wait for query to complete
            import time
            while True:
                result = logs_client.get_query_results(queryId=query_id)
                
                if result['status'] == 'Complete':
                    logs = []
                    for record in result['results']:
                        log_entry = {}
                        for field in record:
                            log_entry[field['field']] = field['value']
                        logs.append(log_entry)
                    return logs
                
                elif result['status'] == 'Failed':
                    return []
                
                time.sleep(1)
        
        except logs_client.exceptions.ResourceNotFoundException:
            # Log group doesn't exist yet
            return []
    
    except Exception as e:
        print(f"Error retrieving logs: {e}", file=sys.stderr)
        return []


def display_logs(logs: list, job_id: str):
    """Display logs in formatted output."""
    if not logs:
        print(f"No logs found for job {job_id}")
        return
    
    print(f"\nLogs for job {job_id}")
    print("=" * 80)
    
    for log in logs:
        timestamp = log.get('@timestamp', 'N/A')
        message = log.get('@message', '')
        stream = log.get('@logStream', 'N/A')
        
        # Format output
        print(f"[{timestamp}] {stream}")
        print(f"  {message}")
    
    print()


def follow_logs(session: boto3.Session, job_id: str, config: dict, start_time: datetime):
    """Follow logs in real-time."""
    import time
    
    print(f"\nFollowing logs for job {job_id} (Ctrl+C to stop)...\n")
    
    last_timestamp = start_time
    
    try:
        while True:
            logs = retrieve_logs(session, job_id, config, start_time=last_timestamp, max_lines=50)
            
            if logs:
                for log in reversed(logs):
                    timestamp = log.get('@timestamp', 'N/A')
                    message = log.get('@message', '')
                    print(f"[{timestamp}] {message}")
                
                # Update last timestamp
                if logs:
                    last_entry_time = logs[0].get('@timestamp', '')
                    if last_entry_time:
                        last_timestamp = datetime.fromisoformat(last_entry_time.replace('Z', '+00:00'))
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopped following logs.")


def parse_time_offset(offset_str: str) -> datetime:
    """
    Parse time offset string like '10m', '1h', '30s'.
    Returns datetime object.
    """
    pattern = r'^(\d+)([smhd])$'
    match = re.match(pattern, offset_str.lower())
    
    if not match:
        raise ValueError(f"Invalid time offset: {offset_str}. Use format like '10m', '1h', etc.")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    now = get_utc_time()
    
    if unit == 's':
        return now - timedelta(seconds=amount)
    elif unit == 'm':
        return now - timedelta(minutes=amount)
    elif unit == 'h':
        return now - timedelta(hours=amount)
    elif unit == 'd':
        return now - timedelta(days=amount)
    else:
        raise ValueError(f"Unknown time unit: {unit}")


def get_utc_time() -> datetime:
    """Get current UTC time."""
    return datetime.utcnow()


def get_utc_time_minus(minutes: int = 0, hours: int = 0, days: int = 0) -> datetime:
    """Get UTC time minus specified duration."""
    return datetime.utcnow() - timedelta(minutes=minutes, hours=hours, days=days)


if __name__ == '__main__':
    main()
