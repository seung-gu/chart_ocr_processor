"""GitHub Actions workflow: Complete data collection pipeline.

This script runs the full workflow:
1. Download new FactSet PDFs
2. Extract EPS chart pages as PNGs
3. Process images and extract data to CSV
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.data_collection.download_factset_pdfs import download_factset_pdfs, main as download_main
from scripts.data_collection.extract_eps_charts import main as extract_main
from src.chart_ocr_processor.processor import process_directory


def main():
    """Run complete data collection workflow."""
    print("=" * 80)
    print("🚀 FactSet Data Collection Workflow")
    print("=" * 80)
    print()
    
    # Step 1: Download PDFs
    print("📥 Step 1: Downloading FactSet PDFs...")
    print("-" * 80)
    try:
        download_main()
        print("✅ PDF download complete\n")
    except Exception as e:
        print(f"❌ PDF download failed: {e}\n")
        return
    
    # Step 2: Extract PNGs
    print("🖼️  Step 2: Extracting EPS chart pages...")
    print("-" * 80)
    try:
        extract_main()
        print("✅ PNG extraction complete\n")
    except Exception as e:
        print(f"❌ PNG extraction failed: {e}\n")
        return
    
    # Step 3: Process images
    print("🔍 Step 3: Processing images and extracting data...")
    print("-" * 80)
    try:
        estimates_dir = PROJECT_ROOT / "output" / "estimates"
        output_csv = PROJECT_ROOT / "output" / "extracted_estimates.csv"
        
        df = process_directory(
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
    
    print("=" * 80)
    print("✨ Workflow complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

