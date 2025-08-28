# GSH_Automation

GSH_Automation is a bioinformatics automation pipeline designed to
simplify the downloading, preprocessing, and preparation of genomic
datasets from multiple sources like Ensembl, COSMIC, miRGene, Orthologs,
EnhancerAtlas, UCSC, and more.\
This repository provides a **choice-based menu system** (`main.py`) to
enable users to selectively execute tasks, ensuring modularity and
control over each dataset.

------------------------------------------------------------------------

## Features

-   **Automated Data Downloads**: Fetch genomic and annotation datasets
    from trusted sources (Ensembl, COSMIC, miRGene, EnhancerAtlas, UCSC,
    etc.).\
-   **Choice-Based Menu System**: Interactive CLI for step-by-step
    control over data downloads and processing.\
-   **Environment Setup**: Easy setup via Conda with required
    dependencies listed.\
-   **Modular Scripts**: Each dataset and preprocessing step is isolated
    in its own module under the `scripts/` folder.

------------------------------------------------------------------------

## Folder Structure

``` bash
GSH_Automation/
│
├── main.py                 # Entry point for running the pipeline (choice-based menu system)
├── scripts/                # Contains all modular scripts for downloading/processing data
│   ├── ensembl.py          # Downloads Ensembl dataset
│   ├── cosmic.py           # Downloads COSMIC dataset
│   ├── mirgene.py          # Downloads miRGene dataset
│   ├── orthologs.py        # Downloads Orthologs data
│   ├── enhanceratlas.py    # Downloads EnhancerAtlas data
│   ├── liftover.py         # Runs UCSC Liftover for genome coordinate mapping
│   ├── cosmic_env.py       # Handles COSMIC environment-specific downloads
│   ├── rna_files.py        # Downloads lncRNA and tRNA files
│   ├── gaps_ftp.py         # Downloads UCSC Gaps FTP data
│   └── wget.py             # Downloads additional chromosome info via WGET
│
└── README.md               # Documentation (this file)
```

------------------------------------------------------------------------

## Choice-Based Menu System

The **`main.py`** script provides an **interactive choice-based menu
system**.\
This design ensures flexibility by letting users run specific tasks
independently instead of executing the entire pipeline at once.

### Example Menu

    ==== Choose from the Menu ====
    1. Download Ensembl data
    2. Download miRGene data
    3. Download Orthologs data
    4. Download COSMIC data
    5. Download EnhancerAtlas (retain dr.bed)
    6. Run Liftover on dr.bed file
    7. Download lncRNA and tRNA files
    8. USCS_Gaps_FTP
    9. WGET
    10. Exit

-   Enter the corresponding number to run a specific module.
-   Example: typing `1` runs the Ensembl download script
    (`scripts/ensembl.py`).
-   You can perform multiple tasks in sequence, and exit the pipeline
    anytime by choosing option `10`.

------------------------------------------------------------------------

## Setup Instructions

### 1. Clone the Repository

``` bash
git clone https://github.com/TheOfficialBug/GSH_Automation.git
cd GSH_Automation
```

### 2. Create a Conda Environment

We recommend using Conda to manage dependencies.

``` bash
conda create -n gsh_env python=3.9 -y
conda activate gsh_env
```

### 3. Install Dependencies

Install required Python packages:

``` bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install packages as needed
(e.g., `requests`, `biopython`, etc.).

------------------------------------------------------------------------

## Running the Pipeline

Run the main script to start the choice-based menu system:

``` bash
python main.py
```

Follow the on-screen prompts to download and process datasets as
required.

------------------------------------------------------------------------

## Notes

-   Ensure you have a stable internet connection while downloading
    datasets.\
-   For COSMIC data, you may need special access permissions depending
    on the dataset.\
-   Logs can optionally be saved using utilities in `utils/logger.py`
    (currently commented out in `main.py`).

------------------------------------------------------------------------
