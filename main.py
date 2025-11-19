"""Local execution: Process images with OCR.

This script provides a local entry point for processing chart images.
For programmatic use, import from the main package:
    from factset_data_collector import process_images
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.factset_data_collector import process_images


def main():
    """Main entry point for local image processing."""
    # Default paths
    estimates_dir = PROJECT_ROOT / "output" / "estimates"
    output_csv = PROJECT_ROOT / "output" / "extracted_estimates.csv"
    
    print("=" * 80)
    print("FactSet Data Processor (Local)")
    print("=" * 80)
    print()
    
    # Process images
    df = process_images(
        directory=estimates_dir,
        output_csv=output_csv,
        use_coordinate_matching=True,
        classify_bars=True,
        use_multiple_methods=True
    )
    
    print()
    print("=" * 80)
    print(f"✅ Complete: {len(df)} records processed")
    print(f"   Output: {output_csv}")
    print("=" * 80)


if __name__ == '__main__':
    main()
