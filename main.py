"""
GSH Pipeline - Main Entry Point
Genomic Safe Harbor Identification Pipeline
AWS Hybrid Deployment Implementation

Report: GSH Pipeline: AWS Hybrid Deployment - Term Project Report
Based on: Aznauryan et al., Genome Biology and Evolution, 2016

This module provides the main pipeline orchestration for identifying
intergenic and non-regulatory regions suitable for safe genetic integration.

Container Information:
- Docker 20.10+
- Python 3.9
- BEDOPS 2.4.39
- BEDTools 2.30
"""

import os
import sys
from pathlib import Path

# Import pipeline components
from scripts import ensembl, cosmic, mirgene, orthologs, enhanceratlas, liftover, cosmic_env, rna_files, gaps_ftp, wget

def menu():
    """
    Interactive menu for GSH Pipeline operations.
    
    Note: For production deployments in AWS hybrid architecture,
    the pipeline is invoked by the Local Agent via Docker container,
    not through this interactive menu.
    """
    while True:
        print("\n" + "="*60)
        print("GSH PIPELINE - GENOMIC SAFE HARBOR IDENTIFICATION")
        print("Hybrid AWS Deployment - Version 1.0.0")
        print("="*60)
        print("\n==== Choose from the Menu ====")
        print("1. Download Ensembl data")
        print("2. Download miRGene data")
        print("3. Download Orthologs data")
        print("4. Download COSMIC data")
        print("5. Download EnhancerAtlas (retain dr.bed)")
        print("6. Run Liftover on dr.bed file")
        print("7. Download lncRNA and tRNA files")
        print("8. USCS_Gaps_FTP")
        print("9. WGET")
        print("10. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == '1': ensembl.download()
        elif choice == '2': mirgene.download()
        elif choice == '3': orthologs.download()
        elif choice == '4': cosmic.download()
        elif choice == '5': enhanceratlas.download()
        elif choice == '6': liftover.run()
        elif choice == '7': rna_files.main()
        elif choice == '8': gaps_ftp.download_ucsc_gap_data()
        elif choice == '9': wget.download_chrominfo()
        elif choice == '10': 
            print("Exiting GSH Pipeline. Goodbye!")
            break
        else: 
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    """
    Entry point for GSH Pipeline.
    
    PRODUCTION DEPLOYMENT:
    This pipeline runs within Docker containers as part of the AWS Hybrid
    architecture. The Local Agent submits jobs to this pipeline with parameters:
    
      docker run -e JOB_ID=<id> -e RESEARCHER_ID=<id> \\
        -e DIST_FROM_GENES=<int> -e INCLUDE_ENHANCERS=<bool> \\
        -e INCLUDE_MIRNAS=<bool> -v /data/input:/data/input \\
        -v /data/output:/data/output gsh-pipeline:latest
    
    Output files are written to /data/output:
      - gsh_candidates.bed: Safe harbor candidate regions
      - gsh_sequences.fasta: FASTA sequences of candidates
      - metrics.json: Analysis metrics and statistics
    
    For development/testing: Run menu() for interactive mode
    For production: Use Docker container with environment variables
    """
    
    # Check if running in container with environment variables
    job_id = os.environ.get('JOB_ID')
    
    if job_id:
        # Production containerized execution
        print(f"GSH Pipeline - Production Container Mode")
        print(f"Job ID: {job_id}")
        print(f"Researcher: {os.environ.get('RESEARCHER_ID', 'unknown')}")
        # TODO: Implement automated pipeline execution based on environment variables
        # This would run non-interactively with parameters from Local Agent
        menu()  # Fallback to menu for now
    else:
        # Development/testing - interactive menu
        menu()
