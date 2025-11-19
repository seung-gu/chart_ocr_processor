"""Test that process_directory properly maintains existing data and updates both CSVs."""

import sys
from pathlib import Path
import pandas as pd
import tempfile
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.factset_data_collector.core.ocr.processor import process_directory


def test_existing_data_preserved():
    """Test that existing CSV data is preserved when processing new images."""
    
    # Mock cloud CSV reads
    existing_main = pd.DataFrame({
        'Report_Date': ['2016-12-09', '2016-12-16'],
        'Q1\'14': [27.85, 27.90],
        'Q2\'14': [29.67, 29.70]
    })
    
    existing_confidence = pd.DataFrame({
        'Report_Date': ['2016-12-09', '2016-12-16'],
        'Confidence': [85.5, 87.0]
    })
    
    # Mock process_image to return new data
    def mock_process_image(image_path):
        # Return data for a new date
        return [{
            'report_date': '2016-12-23',
            'quarter': 'Q1\'14',
            'eps': 28.0,
            'bar_color': 'dark',
            'bar_confidence': 'high'
        }, {
            'report_date': '2016-12-23',
            'quarter': 'Q2\'14',
            'eps': 30.0,
            'bar_color': 'dark',
            'bar_confidence': 'high'
        }]
    
    with patch('src.factset_data_collector.core.ocr.processor.read_csv_from_cloud') as mock_read:
        def read_side_effect(path):
            if path == 'extracted_estimates.csv':
                return existing_main.copy()
            elif path == 'extracted_estimates_confidence.csv':
                return existing_confidence.copy()
            return None
        
        mock_read.side_effect = read_side_effect
        
        # Create temp directory with one image
        test_dir = Path(tempfile.mkdtemp())
        test_image = test_dir / '20161223-6.png'
        test_image.touch()
        
        with patch('src.factset_data_collector.core.ocr.processor.process_image', side_effect=mock_process_image):
            main_df, conf_df = process_directory(test_dir)
        
        # Assertions
        assert len(main_df) == 3, f"Expected 3 records (2 existing + 1 new), got {len(main_df)}"
        assert len(conf_df) == 3, f"Expected 3 confidence records, got {len(conf_df)}"
        
        # Check existing dates preserved
        dates = main_df['Report_Date'].tolist()
        assert '2016-12-09' in dates, "Existing date 2016-12-09 should be preserved"
        assert '2016-12-16' in dates, "Existing date 2016-12-16 should be preserved"
        assert '2016-12-23' in dates, "New date 2016-12-23 should be added"
        
        # Check existing values preserved
        row_1 = main_df[main_df['Report_Date'] == '2016-12-09'].iloc[0]
        assert row_1['Q1\'14'] == 27.85, "Existing Q1'14 value should be preserved"
        
        # Check new values added
        row_new = main_df[main_df['Report_Date'] == '2016-12-23']
        if row_new.empty:
            print(f"❌ ERROR: New row not found! Available dates: {main_df['Report_Date'].tolist()}")
            print(f"   Main DF columns: {main_df.columns.tolist()}")
            print(f"   Main DF:\n{main_df}")
            assert False, "New date 2016-12-23 not found in results"
        
        row_new = row_new.iloc[0]
        q1_val = row_new.get('Q1\'14', 'MISSING')
        assert float(q1_val) == 28.0, f"New Q1'14 value should be 28.0, got {q1_val}"
        
        # Check confidence preserved
        conf_dates = conf_df['Report_Date'].tolist()
        assert '2016-12-09' in conf_dates, "Existing confidence date should be preserved"
        assert conf_df[conf_df['Report_Date'] == '2016-12-09'].iloc[0]['Confidence'] == 85.5, \
            "Existing confidence value should be preserved"
        
        print("✅ All assertions passed! Existing data is preserved correctly.")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)


def test_both_csvs_returned():
    """Test that process_directory returns both main and confidence DataFrames."""
    
    existing_main = pd.DataFrame({
        'Report_Date': ['2016-12-09'],
        'Q1\'14': [27.85]
    })
    
    existing_confidence = pd.DataFrame({
        'Report_Date': ['2016-12-09'],
        'Confidence': [85.5]
    })
    
    with patch('src.factset_data_collector.core.ocr.processor.read_csv_from_cloud') as mock_read:
        def read_side_effect(path):
            if path == 'extracted_estimates.csv':
                return existing_main.copy()
            elif path == 'extracted_estimates_confidence.csv':
                return existing_confidence.copy()
            return None
        
        mock_read.side_effect = read_side_effect
        
        test_dir = Path(tempfile.mkdtemp())
        
        # No images to process
        main_df, conf_df = process_directory(test_dir)
        
        # Should return existing data
        assert isinstance(main_df, pd.DataFrame), "Should return main DataFrame"
        assert isinstance(conf_df, pd.DataFrame), "Should return confidence DataFrame"
        assert len(main_df) == 1, "Should return existing main data"
        assert len(conf_df) == 1, "Should return existing confidence data"
        
        print("✅ Both CSVs are returned correctly.")
        
        import shutil
        shutil.rmtree(test_dir)


def test_empty_cloud_handling():
    """Test handling when cloud CSV doesn't exist."""
    
    with patch('src.factset_data_collector.core.ocr.processor.read_csv_from_cloud') as mock_read:
        mock_read.return_value = None
        
        test_dir = Path(tempfile.mkdtemp())
        
        main_df, conf_df = process_directory(test_dir)
        
        # Should return empty DataFrames with Report_Date column
        assert isinstance(main_df, pd.DataFrame), "Should return DataFrame"
        assert isinstance(conf_df, pd.DataFrame), "Should return DataFrame"
        assert 'Report_Date' in main_df.columns, "Should have Report_Date column"
        assert 'Report_Date' in conf_df.columns, "Should have Report_Date column"
        
        print("✅ Empty cloud handling works correctly.")
        
        import shutil
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("=" * 80)
    print("Testing CSV Update Functionality")
    print("=" * 80)
    
    try:
        test_existing_data_preserved()
        print()
        test_both_csvs_returned()
        print()
        test_empty_cloud_handling()
        
        print("\n" + "=" * 80)
        print("✨ All tests passed!")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

