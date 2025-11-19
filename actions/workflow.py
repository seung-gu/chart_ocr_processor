"""GitHub Actions workflow: Complete data collection pipeline.

This script runs the full workflow:
1. Download CSV from cloud
2. Check for new PDFs
3. Download new PDFs if available
4. Extract EPS chart pages as PNGs
5. Process images and extract data to CSV
6. Upload results to cloud
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.factset_data_collector import download_pdfs, extract_charts, process_images
from src.factset_data_collector.utils import (
    CLOUD_STORAGE_ENABLED,
    download_from_cloud,
    list_cloud_files,
    upload_to_cloud,
)


def main():
    """Run complete data collection workflow."""
    print("=" * 80)
    print("🚀 FactSet Data Collection Workflow")
    print("=" * 80)
    print()
    
    # Only run cloud workflow in CI environment
    if not CLOUD_STORAGE_ENABLED:
        print("⚠️  Cloud storage not enabled. This workflow is for CI environment only.")
        print("   For local execution, use individual scripts or main.py")
        return
    
    # Step 0: Download CSV from cloud
    print("-" * 80)
    print(" 📥 Step 0: Downloading CSV from cloud...")
    
    csv_file = PROJECT_ROOT / "output" / "extracted_estimates.csv"
    confidence_csv_file = PROJECT_ROOT / "output" / "extracted_estimates_confidence.csv"
    
    csv_downloaded = download_from_cloud("extracted_estimates.csv", csv_file)
    confidence_downloaded = download_from_cloud("extracted_estimates_confidence.csv", confidence_csv_file)
    
    if csv_downloaded:
        print(f"✅ Downloaded CSV from cloud: {csv_file}")
    else:
        print("ℹ️  No CSV found in cloud (first run)")
    
    if confidence_downloaded:
        print(f"✅ Downloaded confidence CSV from cloud: {confidence_csv_file}")
    else:
        print("ℹ️  No confidence CSV found in cloud (first run)")
    
    print()
    
    # Step 1: Check for new PDFs
    print("-" * 80)
    print(" 🔍 Step 1: Checking for new PDFs...")
    
    # Get last date from CSV
    last_date = None
    if csv_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_file)
            if not df.empty and 'Report_Date' in df.columns:
                df['Report_Date'] = pd.to_datetime(df['Report_Date'])
                last_date = df['Report_Date'].max().to_pydatetime()
                print(f"📅 Last report date in CSV: {last_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"⚠️  Could not read CSV: {e}")
    
    # Get cloud PDF list
    cloud_pdfs = list_cloud_files('reports/')
    cloud_pdf_names = {Path(p).name for p in cloud_pdfs}
    print(f"📦 Found {len(cloud_pdf_names)} PDFs in cloud")
    
    # Download new PDFs
    print("-" * 80)
    print(" 📥 Step 2: Downloading new PDFs from FactSet...")
    
    try:
        pdf_dir = PROJECT_ROOT / "output" / "factset_pdfs"
        pdfs = download_pdfs(
            start_date=datetime(2016, 1, 1),
            end_date=datetime.now(),
            outpath=pdf_dir,
            rate_limit=0.05
        )
        
        # Check if any new PDFs were downloaded
        local_pdfs = list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else []
        new_pdfs = [p for p in local_pdfs if p.name not in cloud_pdf_names]
        
        if not new_pdfs:
            print("\n✅ No new PDFs to process. Workflow complete!")
            return
        
        print(f"✅ Downloaded {len(new_pdfs)} new PDF(s)\n")
    except Exception as e:
        print(f"❌ PDF download failed: {e}\n")
        return
    
    # Step 3: Extract PNGs
    print("-" * 80)
    print(" 🖼️  Step 3: Extracting EPS chart pages...")
    
    try:
        estimates_dir = PROJECT_ROOT / "output" / "estimates"
        charts = extract_charts(local_pdfs, outpath=estimates_dir)
        print(f"✅ PNG extraction complete: {len(charts)} charts\n")
    except Exception as e:
        print(f"❌ PNG extraction failed: {e}\n")
        return
    
    # Step 4: Process images
    print("-" * 80)
    print(" 🔍 Step 4: Processing images and extracting data...")
    
    try:
        output_csv = PROJECT_ROOT / "output" / "extracted_estimates.csv"
        
        df = process_images(
            directory=estimates_dir,
            output_csv=output_csv,
            use_coordinate_matching=True,
            classify_bars=True,
            use_multiple_methods=True
        )
        print(f"✅ Image processing complete: {len(df)} records\n")
    except Exception as e:
        print(f"❌ Image processing failed: {e}\n")
        return
    
    # Step 5: Upload to cloud
    print("-" * 80)
    print(" ☁️  Step 5: Uploading results to cloud...")
    
    # Upload new PDFs
    uploaded_pdfs = 0
    if pdf_dir.exists():
        for pdf_file in pdf_dir.glob("*.pdf"):
            if pdf_file.name not in cloud_pdf_names:
                cloud_path = f"reports/{pdf_file.name}"
                if upload_to_cloud(pdf_file, cloud_path):
                    uploaded_pdfs += 1
    print(f"✅ Uploaded {uploaded_pdfs} PDF(s) to cloud")
    
    # Upload new PNGs
    uploaded_pngs = 0
    if estimates_dir.exists():
        cloud_pngs = {Path(p).name for p in list_cloud_files('estimates/')}
        for png_file in estimates_dir.glob("*.png"):
            if png_file.name not in cloud_pngs:
                cloud_path = f"estimates/{png_file.name}"
                if upload_to_cloud(png_file, cloud_path):
                    uploaded_pngs += 1
    print(f"✅ Uploaded {uploaded_pngs} PNG(s) to cloud")
    
    # Upload CSV files
    if csv_file.exists():
        if upload_to_cloud(csv_file, "extracted_estimates.csv"):
            print("✅ Uploaded CSV to cloud")
    
    if confidence_csv_file.exists():
        if upload_to_cloud(confidence_csv_file, "extracted_estimates_confidence.csv"):
            print("✅ Uploaded confidence CSV to cloud")
    
    print()
    print("=" * 80)
    print("✨ Workflow complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
