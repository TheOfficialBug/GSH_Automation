# GSH Pipeline - Genomic Safe Harbor Identification

**Scalable and Secure Genomic Safe Harbor Identification Pipeline**  
**Using Hybrid AWS Architecture**

Based on: [GSH Pipeline: AWS Hybrid Deployment - Term Project Report](../DEPLOYMENT_GUIDE.md)  
Authors: [Your Names]  
Institution: University of Pennsylvania | UT Austin | Iowa State University  
Date: May 2026

------------------------------------------------------------------------

## Overview

GSH (Genomic Safe Harbor) Pipeline is an automated bioinformatics platform for identifying intergenic and non-regulatory regions suitable for safe genetic integration in *Danio rerio* (zebrafish). The pipeline simplifies the downloading, preprocessing, and analysis of genomic datasets from multiple sources including Ensembl, COSMIC, miRGene, Orthologs, EnhancerAtlas, UCSC, and more.

This implementation features:
- **Containerized Deployment**: Docker ensures reproducibility across environments
- **Hybrid AWS Architecture**: Cloud coordination with on-premises data processing
- **Multi-Institutional Access**: Enable researchers across Penn, UT Austin, and Iowa State
- **Defense-in-Depth Security**: Encryption, access control, and audit logging
- **Cost Efficiency**: 30x cheaper than traditional on-premise infrastructure

------------------------------------------------------------------------

## Architecture

### Hybrid Design

```
┌─────────────────────────┐         ┌──────────────────────────┐
│   Campus Networks       │         │   AWS Cloud (Region)     │
│                         │         │                          │
│  ┌──────────────────┐   │         │  ┌───────────────────┐   │
│  │  Genome Files    │   │         │  │  Lambda Validator │   │
│  │  (Local Storage) │   │         │  │  (Job validation) │   │
│  └──────────────────┘   │         │  └───────────────────┘   │
│           ▲             │         │           ▲              │
│           │             │         │           │              │
│  ┌──────────────────┐   │         │  ┌───────────────────┐   │
│  │  Local Agent     │◄──┼─────────┼─►│     SQS Queue     │   │
│  │  (Polling Job)   │   │Encrypted│  │  (Job Storage)    │   │
│  └──────────────────┘   │ Tunnel  │  └───────────────────┘   │
│           ▲             │(AES-256)│           ▲              │
│           │             │         │           │              │
│  ┌──────────────────┐   │         │  ┌───────────────────┐   │
│  │  Docker Engine   │   │         │  │  CloudWatch       │   │
│  │  (Pipeline Exec) │   │         │  │  (Audit Logging)  │   │
│  └──────────────────┘   │         │  └───────────────────┘   │
│                         │         │                          │
└─────────────────────────┘         └──────────────────────────┘
   Data Locality                      Cloud Coordination
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Pipeline Core** | Python 3.9 + BEDOPS + BEDTools | Genomic analysis |
| **Containerization** | Docker 20.10+ | Reproducible execution |
| **Container Registry** | AWS ECR | Image storage |
| **Local Agent** | Python 3.8+ boto3 | Job polling & execution |
| **Job Queue** | AWS SQS | Persistent messaging |
| **Validation** | AWS Lambda (Python 3.9) | Parameter validation |
| **Notifications** | Lambda + SES | Email reporting |
| **Monitoring** | AWS CloudWatch | Logs & metrics |
| **Encryption** | KMS + AES-256 | Data protection |
| **Access Control** | AWS IAM + STS | Role-based security |

------------------------------------------------------------------------

## Features

### Data Pipeline
- **Automated Data Downloads**: Fetch genomic datasets from Ensembl, COSMIC, miRGene, EnhancerAtlas, UCSC, etc.
- **Choice-Based Menu System**: Interactive CLI for step-by-step control over data processing
- **Modular Architecture**: Each dataset and preprocessing step isolated in its own module
- **Data Filtering**: Apply biological constraints (distance from genes, enhancers, miRNAs)

### Infrastructure
- **Multi-Institutional Access**: Unified web portal across three universities
- **Data Locality**: Genomic data remains on campus (no costly uploads)
- **Containerized Reproducibility**: Identical outputs across different campus environments
- **Scalable Design**: Independent campus agents enable natural parallelism
- **Security**: Defense-in-depth with encryption, IAM, and audit trails
- **Cost Efficiency**: ~$112/month vs $3,350/month on-premise (30x savings)

------------------------------------------------------------------------

## Folder Structure

```
.
├── DEPLOYMENT_GUIDE.md          # Complete deployment and usage guide
├── GSH_Automation/              # Core pipeline code
│   ├── main.py                  # Interactive menu (dev/testing)
│   ├── local_agent.py           # AWS Local Agent service
│   ├── gsh_submit.py            # CLI tool for job submission
│   ├── gsh_status.py            # CLI tool for status checking
│   ├── gsh_logs.py              # CLI tool for log retrieval
│   ├── Dockerfile               # Container definition
│   ├── requirements.txt          # Python dependencies
│   ├── config.template.json     # Configuration template
│   ├── scripts/                 # Modular data download scripts
│   │   ├── ensembl.py           # Ensembl dataset
│   │   ├── cosmic.py            # COSMIC dataset
│   │   ├── mirgene.py           # miRGene dataset
│   │   ├── orthologs.py         # Ortholog data
│   │   ├── enhanceratlas.py     # EnhancerAtlas regions
│   │   ├── liftover.py          # Coordinate liftover
│   │   ├── rna_files.py         # lncRNA/tRNA files
│   │   ├── gaps_ftp.py          # UCSC Gaps data
│   │   └── wget.py              # Additional downloads
│   └── settings.py              # Configuration
│
└── gsh-deployment/              # AWS infrastructure
    ├── lambda_job_validator.py  # Lambda: Job validation
    ├── lambda_notification_handler.py  # Lambda: Email notifications
    ├── infrastructure/
    │   └── cloudformation.yaml  # IaC template (SQS, Lambda, IAM, KMS, etc.)
    └── package.json             # Node dependencies
```

------------------------------------------------------------------------

## Quick Start

### For Administrators

1. **Read the Deployment Guide**:
   ```bash
   cat ../DEPLOYMENT_GUIDE.md
   ```

2. **Follow Administrator Setup (Section 2)**:
   - Install prerequisites
   - Configure AWS credentials
   - Build and push Docker image
   - Deploy Lambda functions
   - Start Local Agent service

### For Researchers

#### Option A: Web Portal (Recommended)
1. Navigate to https://gsh-pipeline.edu
2. Authenticate with university credentials
3. Submit job with genome path and parameters
4. Monitor progress on dashboard
5. Download results when complete

#### Option B: Command-Line Interface
```bash
# Submit job
gsh-submit --genome /data/genomes/danio_rerio.bed --dist-genes 50000

# Check status
gsh-status a1b2c3d4-e5f6-7890-abcd-ef1234567890

# View logs
gsh-logs a1b2c3d4-e5f6-7890-abcd-ef1234567890 --follow
```

------------------------------------------------------------------------

## Development

### Local Testing

For development and testing, use the interactive menu system:

```bash
# Create environment
conda create -n gsh_dev python=3.9 -y
conda activate gsh_dev

# Install dependencies
pip install -r requirements.txt

# Run interactive menu
python main.py
```

### Production Deployment

The pipeline runs in Docker containers orchestrated by the Local Agent:

```bash
# Build container
docker build -t gsh-pipeline:latest .

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/gsh-pipeline:latest

# Deploy infrastructure
cd gsh- -deployment
aws cloudformation deploy \
  --template-file infrastructure/cloudformation.yaml \
  --stack-name gsh-pipeline \
  --capabilities CAPABILITY_NAMED_IAM
```

------------------------------------------------------------------------

## Configuration

Copy the configuration template and customize for your campus:

```bash
cp config.template.json ~/.gsh/config.json
# Edit ~/.gsh/config.json with:
#  - AWS account ID and region
#  - SQS queue URL
#  - ECR registry URI
#  - Local genome file paths
#  - Institution-specific settings
```

------------------------------------------------------------------------

## Security

### Encryption
- **In Transit**: AES-256 via PrivateLink/VPN (NIST FIPS 197)
- **At Rest**: AWS KMS managed keys for S3 storage
- **Local Filesystem**: Campus IT controls physical security

### Access Control
- **Authentication**: AWS IAM with time-limited tokens (1-hour TTL)
- **Authorization**: Path-based isolation (/jobs/researcher/*)
- **Audit Logging**: CloudWatch logs all system events
- **Defense-in-Depth**: Multiple security layers

### Compliance
- **HIPAA**: Supports HIPAA requirements for genomic data
- **IRB**: Meets institutional review board standards
- **Data Sovereignty**: Raw genomic data never leaves campus

------------------------------------------------------------------------

## Performance & Costs

### Execution Times
- **Pipeline Runtime**: 5-35 minutes (depending on genome size)
- **End-to-End**: <40 minutes from submission to results
- **Lambda Response**: ~2 seconds per request

### Cost Analysis (50 jobs/month)
- Lambda: $1
- SQS: $0.40
- CloudWatch: $10
- S3: $100
- **Total: $112/month** (vs $3,350/month on-premise)

------------------------------------------------------------------------

## References

[1] Aznauryan, E., et al. "Discovery and Validation of Genomic Safe Harbors." *Genome Biology and Evolution*, 2016.  
[2] NIST. "FIPS 197: Advanced Encryption Standard (AES)." 2001.  
[3] Amazon Web Services. "AWS Lambda Developer Guide." https://docs.aws.amazon.com/lambda/  
[4] Amazon Web Services. "AWS IAM User Guide." https://docs.aws.amazon.com/iam/  
[5] Amazon Web Services. "AWS CloudWatch User Guide." https://docs.aws.amazon.com/cloudwatch/  
[6] Quinlan, A. R. and Hall, I. M. "BEDTools: utilities for genomic features." *Bioinformatics*, 2010.  
[7] Neph, S., et al. "BEDOPS: high-performance genomic feature operations." *Bioinformatics*, 2012.  
[8] Merkel, D. "Docker: Lightweight Linux Containers." *Linux Journal*, 2014.  

------------------------------------------------------------------------

## Support

- **Documentation**: See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- **Issues**: Submit to project GitHub repository
- **Email**: gsh-support@[domain].edu
- **Status Page**: https://status.gsh-pipeline.edu

------------------------------------------------------------------------

## Version History

- **1.0.0** (May 2026): Initial release
  - Hybrid AWS architecture
  - Multi-institutional support
  - Containerized pipeline
  - Full security implementation

------------------------------------------------------------------------

## Authors

[Name 1] - AWS Infrastructure (Lambda, SQS, IAM, VPC) - 40%  
[Name 2] - Local Agent & Docker - 35%  
[Name 3] - Encryption & Audit Logging - 25%  

University of Pennsylvania | UT Austin | Iowa State University

------------------------------------------------------------------------

#   G S H _ A W S - H y b r i d  
 