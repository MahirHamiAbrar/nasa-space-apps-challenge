#!/usr/bin/env python3
"""
Quick test script for generate_final_output.py
Creates sample data and runs the pipeline.
"""
import pandas as pd
import os
import subprocess
import sys

def create_sample_data():
    """
    Create sample standard format files for testing.
    """
    print("Creating sample data files...")
    
    os.makedirs('data', exist_ok=True)
    
    # Sample candidates
    candidates = pd.DataFrame({
        'mission': ['Kepler', 'Kepler', 'Kepler', 'Kepler', 'TESS', 'TESS'],
        'object_name': ['K00711.03', 'K01501.01', 'K05581.01', 'K00111.02', '1468.01', '219.02'],
        'disposition': ['CANDIDATE', 'CANDIDATE', 'CANDIDATE', 'CANDIDATE', 'CANDIDATE', 'CANDIDATE'],
        'period': [124.524522, 2.617028, 374.878133, 23.668346, 5.285000, 3.943328],
        'planet_radius': [2.690000, 1.570000, 4.270000, 2.320000, 1.890000, 7.968167],
        'star_temp': [5497.000000, 4831.000000, 5636.000000, 5979.000000, 5800.000000, 5314.834165],
        'star_radius': [1.046000, 0.724000, 1.354000, 1.005000, 1.120000, 0.969259],
        'star_mass': [0.988000, 0.706000, 1.103000, 0.913000, 1.050000, 0.246349],
        'discovery_facility': ['Kepler', 'Kepler', 'Kepler', 'Kepler', 'TESS', 'TESS']
    })
    candidates.to_csv('data/all_candidates_standard.csv', index=False)
    print(f"✓ Created data/all_candidates_standard.csv ({len(candidates)} rows)")
    
    # Sample false positives
    false_positives = pd.DataFrame({
        'mission': ['TESS', 'Kepler', 'Kepler', 'K2'],
        'object_name': ['5150.01', 'K07522.01', 'K07333.01', '201367065'],
        'disposition': ['FALSE POSITIVE', 'FALSE POSITIVE', 'FALSE POSITIVE', 'FALSE POSITIVE'],
        'period': [1.757829, 10.116145, 2.037427, 8.521543],
        'planet_radius': [13.943300, 17.210000, 0.900000, 2.100000],
        'star_temp': [6640.000000, 4717.000000, 6356.000000, 5400.000000],
        'star_radius': [2.590000, 0.519000, 1.358000, 0.950000],
        'star_mass': [1.100000, 0.536000, 1.101000, 0.980000],
        'discovery_facility': ['TESS', 'Kepler', 'Kepler', 'K2']
    })
    false_positives.to_csv('data/all_false_positives_standard.csv', index=False)
    print(f"✓ Created data/all_false_positives_standard.csv ({len(false_positives)} rows)")
    
    # Sample predictions
    predictions = pd.DataFrame({
        'object_name': [
            '119.01', '119.02', '121.01', '124.01', '125.04',
            'K00711.03', 'K01501.01', 'K07522.01', 'K07333.01',
            'K05581.01', 'K00111.02', '5150.01', '201367065',
            '1468.01', '219.02'
        ],
        'predicted_probability': [
            0.855043, 0.851574, 0.202328, 0.034818, 0.925812,
            0.923456, 0.887654, 0.123456, 0.234567,
            0.876543, 0.912345, 0.045678, 0.156789,
            0.834567, 0.789012
        ]
    })
    predictions.to_csv('sample_predictions.csv', index=False)
    print(f"✓ Created sample_predictions.csv ({len(predictions)} rows)")
    
    return True

def run_test():
    """
    Run the generate_final_output.py script with sample data.
    """
    print("\n" + "="*70)
    print("TESTING FINAL OUTPUT GENERATOR")
    print("="*70)
    
    # Create sample data
    if not create_sample_data():
        print("✗ Failed to create sample data")
        return False
    
    # Run the script
    print("\n" + "="*70)
    print("Running generate_final_output.py...")
    print("="*70)
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                'generate_final_output.py',
                'sample_predictions.csv',
                '--output', 'data/test_final_output.csv',
                '--threshold', '0.5'
            ],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n✗ Script failed with return code: {result.returncode}")
            return False
        
    except Exception as e:
        print(f"\n✗ Error running script: {e}")
        return False
    
    # Verify output
    print("\n" + "="*70)
    print("VERIFYING OUTPUT")
    print("="*70)
    
    output_file = 'data/test_final_output.csv'
    if not os.path.exists(output_file):
        print(f"✗ Output file not created: {output_file}")
        return False
    
    # Read and display output
    output = pd.read_csv(output_file)
    print(f"\n✓ Output file created: {output_file}")
    print(f"✓ Rows: {len(output)}")
    print(f"\nColumns: {list(output.columns)}")
    print(f"\nDisposition counts:")
    print(output['disposition'].value_counts())
    print(f"\nMission counts:")
    print(output['mission'].value_counts())
    
    print(f"\n📊 Full output preview:")
    print(output.to_string(index=True))
    
    # Validate structure
    required_columns = [
        'mission', 'object_name', 'disposition', 'period',
        'planet_radius', 'star_temp', 'star_radius', 'star_mass',
        'discovery_facility'
    ]
    
    missing_cols = set(required_columns) - set(output.columns)
    if missing_cols:
        print(f"\n✗ Missing required columns: {missing_cols}")
        return False
    
    print("\n✓ All required columns present")
    
    # Check dispositions
    valid_dispositions = {'CONFIRMED', 'FALSE POSITIVE'}
    invalid = set(output['disposition'].unique()) - valid_dispositions
    if invalid:
        print(f"\n✗ Invalid dispositions found: {invalid}")
        return False
    
    print("✓ All dispositions valid")
    
    print("\n" + "="*70)
    print("  ✅ TEST PASSED! Everything working correctly.  ✅")
    print("="*70 + "\n")
    
    return True

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)