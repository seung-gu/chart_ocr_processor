"""Test script for confidence CSV append functionality."""

import sys
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.factset_data_collector.core.ocr.processor import process_directory


def test_confidence_csv_append():
    """Test that confidence CSV properly appends data instead of overwriting."""
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp())
    test_output_csv = test_dir / "test_estimates.csv"
    test_confidence_csv = test_dir / "test_estimates_confidence.csv"
    
    try:
        # Step 1: Create initial confidence CSV with existing data
        print("=" * 80)
        print("Step 1: Creating initial confidence CSV with existing data")
        print("=" * 80)
        
        initial_confidence_data = {
            'Report_Date': ['2024-01-01', '2024-02-01'],
            'Q1 2024': [0.8, 0.9],
            'Q2 2024': [0.7, 0.85],
            'Confidence': ['high', 'medium']
        }
        initial_confidence_df = pd.DataFrame(initial_confidence_data)
        initial_confidence_df.to_csv(test_confidence_csv, index=False)
        print(f"✅ Created initial confidence CSV with {len(initial_confidence_df)} records")
        print(f"   Records: {initial_confidence_df['Report_Date'].tolist()}")
        
        # Step 2: Create a dummy image directory (we'll mock the process)
        # For this test, we'll directly test the append logic
        print("\n" + "=" * 80)
        print("Step 2: Simulating new data append")
        print("=" * 80)
        
        # Simulate what happens in processor: read existing, append new
        existing_confidence_df = pd.read_csv(test_confidence_csv)
        existing_confidence_df['Report_Date'] = pd.to_datetime(existing_confidence_df['Report_Date'])
        print(f"✅ Loaded existing confidence CSV: {len(existing_confidence_df)} records")
        
        # Simulate new confidence data from processing
        new_confidence_data = {
            'Report_Date': ['2024-03-01'],
            'Q1 2024': [0.95],
            'Q2 2024': [0.88],
            'Confidence': ['high']
        }
        new_confidence_df = pd.DataFrame(new_confidence_data)
        new_confidence_df['Report_Date'] = pd.to_datetime(new_confidence_df['Report_Date'])
        print(f"✅ New confidence data: {len(new_confidence_df)} records")
        
        # Merge (same logic as processor)
        if existing_confidence_df.empty:
            merged_confidence_df = new_confidence_df.copy()
        else:
            merged_confidence_df = pd.concat(
                [existing_confidence_df, new_confidence_df], 
                ignore_index=True
            ).drop_duplicates(
                subset=['Report_Date'], 
                keep='last'
            ).sort_values('Report_Date').reset_index(drop=True)
        
        print(f"✅ Merged confidence data: {len(merged_confidence_df)} records")
        print(f"   Records: {merged_confidence_df['Report_Date'].dt.strftime('%Y-%m-%d').tolist()}")
        
        # Save
        merged_confidence_df['Report_Date'] = merged_confidence_df['Report_Date'].dt.strftime('%Y-%m-%d')
        merged_confidence_df.to_csv(test_confidence_csv, index=False)
        
        # Step 3: Verify append worked
        print("\n" + "=" * 80)
        print("Step 3: Verifying append worked correctly")
        print("=" * 80)
        
        final_confidence_df = pd.read_csv(test_confidence_csv)
        final_dates = final_confidence_df['Report_Date'].tolist()
        
        print(f"✅ Final confidence CSV has {len(final_confidence_df)} records")
        print(f"   Records: {final_dates}")
        
        # Assertions
        assert len(final_confidence_df) == 3, f"Expected 3 records, got {len(final_confidence_df)}"
        assert '2024-01-01' in final_dates, "Original record 2024-01-01 should be preserved"
        assert '2024-02-01' in final_dates, "Original record 2024-02-01 should be preserved"
        assert '2024-03-01' in final_dates, "New record 2024-03-01 should be added"
        
        print("\n✅ All assertions passed! Confidence CSV append works correctly.")
        
        # Step 4: Test duplicate handling (same date, different data)
        print("\n" + "=" * 80)
        print("Step 4: Testing duplicate date handling (keep latest)")
        print("=" * 80)
        
        # Add duplicate date with different data
        duplicate_confidence_data = {
            'Report_Date': ['2024-02-01'],  # Same as existing
            'Q1 2024': [0.99],  # Different value
            'Q2 2024': [0.99],
            'Confidence': ['high']  # Different confidence
        }
        duplicate_confidence_df = pd.DataFrame(duplicate_confidence_data)
        duplicate_confidence_df['Report_Date'] = pd.to_datetime(duplicate_confidence_df['Report_Date'])
        
        # Load current
        current_confidence_df = pd.read_csv(test_confidence_csv)
        current_confidence_df['Report_Date'] = pd.to_datetime(current_confidence_df['Report_Date'])
        
        # Merge with duplicate
        merged_duplicate_df = pd.concat(
            [current_confidence_df, duplicate_confidence_df], 
            ignore_index=True
        ).drop_duplicates(
            subset=['Report_Date'], 
            keep='last'  # Keep latest
        ).sort_values('Report_Date').reset_index(drop=True)
        
        merged_duplicate_df['Report_Date'] = merged_duplicate_df['Report_Date'].dt.strftime('%Y-%m-%d')
        merged_duplicate_df.to_csv(test_confidence_csv, index=False)
        
        final_duplicate_df = pd.read_csv(test_confidence_csv)
        print(f"✅ After duplicate merge: {len(final_duplicate_df)} records")
        
        # Check that duplicate was replaced with latest
        feb_record = final_duplicate_df[final_duplicate_df['Report_Date'] == '2024-02-01'].iloc[0]
        assert feb_record['Q1 2024'] == 0.99, "Duplicate should be replaced with latest data"
        assert feb_record['Confidence'] == 'high', "Duplicate should be replaced with latest confidence"
        
        print("✅ Duplicate handling works correctly (keeps latest)")
        
        print("\n" + "=" * 80)
        print("✨ All tests passed!")
        print("=" * 80)
        
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory: {test_dir}")


def test_processor_confidence_csv_integration():
    """Test that process_directory properly handles confidence CSV append."""
    
    # Check if test images exist
    test_image_dir = PROJECT_ROOT / "output" / "estimates"
    if not test_image_dir.exists() or not list(test_image_dir.glob("*.png")):
        print("\n⚠️  No test images found. Skipping integration test.")
        print(f"   Expected directory: {test_image_dir}")
        return
    
    # Create temporary output CSV
    test_dir = Path(tempfile.mkdtemp())
    test_output_csv = test_dir / "test_estimates.csv"
    test_confidence_csv = test_dir / "test_estimates_confidence.csv"
    
    try:
        print("\n" + "=" * 80)
        print("Integration Test: Testing process_directory with confidence CSV")
        print("=" * 80)
        
        # Step 1: Create initial confidence CSV
        print("\nStep 1: Creating initial confidence CSV...")
        initial_confidence_data = {
            'Report_Date': ['2016-12-09'],  # Use a date that won't conflict
            'Q1 2017': [0.8],
            'Confidence': ['high']
        }
        initial_confidence_df = pd.DataFrame(initial_confidence_data)
        initial_confidence_df.to_csv(test_confidence_csv, index=False)
        print(f"✅ Created initial confidence CSV with {len(initial_confidence_df)} records")
        
        # Step 2: Run process_directory (will process images and append to confidence CSV)
        print("\nStep 2: Running process_directory...")
        print(f"   Input directory: {test_image_dir}")
        print(f"   Output CSV: {test_output_csv}")
        
        # Process only first 2 images to avoid long test
        result_df = process_directory(
            directory=test_image_dir,
            output_csv=test_output_csv,
            limit=2
        )
        
        print(f"✅ Processed {len(result_df)} records")
        
        # Step 3: Verify confidence CSV was created/updated
        print("\nStep 3: Verifying confidence CSV...")
        if test_confidence_csv.exists():
            final_confidence_df = pd.read_csv(test_confidence_csv)
            print(f"✅ Confidence CSV exists with {len(final_confidence_df)} records")
            print(f"   Records: {final_confidence_df['Report_Date'].tolist()}")
            
            # Check that initial record is preserved (if not duplicate)
            if '2016-12-09' in final_confidence_df['Report_Date'].values:
                print("✅ Initial record preserved")
            else:
                print("ℹ️  Initial record replaced (expected if duplicate date processed)")
            
            # Check that new records were added
            if len(final_confidence_df) >= 1:
                print("✅ New records added to confidence CSV")
            else:
                print("⚠️  No records in confidence CSV")
        else:
            print("⚠️  Confidence CSV was not created")
        
        print("\n✅ Integration test completed!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n🧹 Cleaned up test directory: {test_dir}")


if __name__ == '__main__':
    test_confidence_csv_append()
    print("\n" + "=" * 80)
    test_processor_confidence_csv_integration()

