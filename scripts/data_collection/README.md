# FactSet Data Collection Guide

This guide explains how to collect and process FactSet data in a local environment.

## 📋 Complete Workflow

Data collection consists of 3 steps:

1. **Download PDFs** - Download Earnings Insight PDFs from FactSet
2. **Extract PNGs** - Extract EPS chart pages from PDFs as PNG images
3. **Extract Data** - Process PNG images to generate CSV data

## 🔧 Prerequisites

### 1. Project Setup

```bash
# From project root
uv sync

# For cloud storage support (GitHub Actions)
uv sync --extra r2
```

### 2. Output Directory Structure

```
output/
├── factset_pdfs/          # Downloaded PDF files
├── estimates/             # Extracted PNG images
├── extracted_estimates.csv              # Main data CSV
└── extracted_estimates_confidence.csv   # Confidence data CSV
```

## 📥 Step 1: Download PDFs

Download FactSet Earnings Insight PDFs.

### Basic Usage

```bash
uv run python scripts/data_collection/download_factset_pdfs.py
```

### Behavior

- **If CSV exists**: Starts downloading from the day after the last date in CSV
- **If CSV doesn't exist**: Downloads all PDFs from 2000-01-01 to today

### Output Locations

- Local: `output/factset_pdfs/`
- Cloud (CI environment): `reports/` (in R2 bucket)

### Examples

```bash
# First run (download all PDFs)
uv run python scripts/data_collection/download_factset_pdfs.py

# Subsequent runs (download only new PDFs)
uv run python scripts/data_collection/download_factset_pdfs.py
```

## 🖼️ Step 2: Extract PNGs

Extract EPS chart pages from downloaded PDFs as PNG images.

### Basic Usage

```bash
uv run python scripts/data_collection/extract_eps_charts.py
```

### Behavior

- **If CSV exists**: Processes only PDFs after the last date in CSV
- **If CSV doesn't exist**: Processes all PDFs
- **If PNG already exists**: Automatically skips

### Output Locations

- Local: `output/estimates/`
- Cloud (CI environment): `estimates/` (in R2 bucket)

### Examples

```bash
# Extract PNGs from PDFs
uv run python scripts/data_collection/extract_eps_charts.py
```

### Notes

- If PDF files are not found, an automatic guidance message will be displayed
- Works normally even if CSV doesn't exist, as long as PDFs are present
- Guidance message: `Please run 'uv run python scripts/data_collection/download_factset_pdfs.py' first to download PDFs.`

## 🔍 Step 3: Extract Data (Image Processing)

Process PNG images to generate CSV data.

### Basic Usage

```bash
uv run python main.py
```

### Arguments

```bash
uv run python main.py [OPTIONS]

Options:
  --input-dir DIR          Image directory (default: output/estimates)
  --output FILE            Output CSV file path (default: output/extracted_estimates.csv)
  --no-coordinate-matching Disable coordinate-based matching
  --no-bar-classification  Disable bar graph classification
  --single-method          Use single method only (1 of 3 methods)
  --limit N                Limit number of images to process (for testing)
```

### Behavior

- **If CSV exists**: Automatically skips images for dates already processed
- **If CSV doesn't exist**: Processes all images
- CSV is automatically updated after each image is processed

### Output Files

- `output/extracted_estimates.csv` - Main data (Report_Date, Quarter columns)
- `output/extracted_estimates_confidence.csv` - Confidence data

### Examples

```bash
# Basic execution
uv run python main.py

# Specify custom directory
uv run python main.py --input-dir output/estimates --output output/my_data.csv

# Test mode (process only 10 images)
uv run python main.py --limit 10

# Disable options
uv run python main.py --no-coordinate-matching --single-method
```

### Notes

- If PNG images are not found, an automatic guidance message will be displayed
- Works normally even if CSV doesn't exist, as long as PNGs are present
- Guidance message: `Please run 'uv run python scripts/data_collection/extract_eps_charts.py' first to extract PNGs from PDFs.`

## 🚀 Complete Workflow Execution

### Local Environment

Execute each step in order:

```bash
# 1. Download PDFs
uv run python scripts/data_collection/download_factset_pdfs.py

# 2. Extract PNGs
uv run python scripts/data_collection/extract_eps_charts.py

# 3. Extract data
uv run python main.py
```

### GitHub Actions (CI Environment)

Execute the complete workflow at once:

```bash
uv run python actions/workflow.py
```

## 📊 Data Format

### Main CSV (`extracted_estimates.csv`)

```
Report_Date,Q1'14,Q2'14,Q3'14,Q4'14,Q1'15,...
2024-11-14,56.45,60.54,62.78,65.78,...
```

### Confidence CSV (`extracted_estimates_confidence.csv`)

```
Report_Date,Confidence
2024-11-14,85.5
```

## ⚠️ Important Notes

1. **Local Execution**: Does not use cloud storage (local files only)
2. **CI Environment**: Cloud storage is automatically used only in GitHub Actions
3. **Order**: Must execute in order: PDF → PNG → CSV
4. **Duplicate Prevention**: Dates already recorded in CSV are automatically skipped

## 🔄 Incremental Updates

All scripts support incremental updates:

- **PDF Download**: Downloads only after the last date in CSV
- **PNG Extraction**: Skips PNGs that already exist
- **Data Extraction**: Skips images for dates already processed

## 📝 Example Scenarios

### Scenario 1: Starting from Scratch

```bash
# 1. Download PDFs (from 2000)
uv run python scripts/data_collection/download_factset_pdfs.py

# 2. Extract PNGs
uv run python scripts/data_collection/extract_eps_charts.py

# 3. Extract data
uv run python main.py
```

### Scenario 2: Updating Only New Data

```bash
# If CSV already exists, each script automatically processes only new data
uv run python scripts/data_collection/download_factset_pdfs.py
uv run python scripts/data_collection/extract_eps_charts.py
uv run python main.py
```

### Scenario 3: Processing Specific Period Only

```bash
# 1. Download PDFs (modify script to specify date range if needed)
uv run python scripts/data_collection/download_factset_pdfs.py

# 2. Extract PNGs
uv run python scripts/data_collection/extract_eps_charts.py

# 3. Extract data (limited count)
uv run python main.py --limit 50
```
