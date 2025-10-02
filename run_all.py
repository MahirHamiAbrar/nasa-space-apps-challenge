#!/usr/bin/env python3
"""
Complete pipeline: Download → Convert → Ready for ML
"""
import sys
import os

def run_pipeline():
    print("\n" + "="*70)
    print("  🚀 NASA SPACE APPS CHALLENGE - EXOPLANET DATA PIPELINE  🪐")
    print("="*70)
    
    # Step 1: Download candidates
    print("\n" + "="*70)
    print("STEP 1: DOWNLOADING CANDIDATES")
    print("="*70)
    try:
        import exoplanet_candidates
        exoplanet_candidates.run_main()
        print("✓ Candidates downloaded!")
    except Exception as e:
        print(f"✗ Error downloading candidates: {e}")
        return False
    
    # Step 2: Download false positives
    print("\n" + "="*70)
    print("STEP 2: DOWNLOADING FALSE POSITIVES")
    print("="*70)
    try:
        import exoplanet_false_positives
        exoplanet_false_positives.run_main()
        print("✓ False positives downloaded!")
    except Exception as e:
        print(f"✗ Error downloading false positives: {e}")
        return False
    
    # Step 3: Convert to standard format
    print("\n" + "="*70)
    print("STEP 3: CONVERTING TO STANDARD FORMAT")
    print("="*70)
    try:
        import convert_to_standard_format
        convert_to_standard_format.run_main()
        print("✓ Data converted to standard format!")
    except Exception as e:
        print(f"✗ Error converting data: {e}")
        return False
    
    # Step 4: Summary
    print("\n" + "="*70)
    print("STEP 4: PIPELINE SUMMARY")
    print("="*70)
    
    try:
        import pandas as pd
        
        # Check output files
        data_folder = 'data'
        
        files_to_check = {
            'All Candidates': f'{data_folder}/all_candidates_standard.csv',
            'All False Positives': f'{data_folder}/all_false_positives_standard.csv',
        }
        
        print("\n📊 Dataset Summary:")
        print("-" * 70)
        
        for name, filepath in files_to_check.items():
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                print(f"\n{name}:")
                print(f"  • File: {filepath}")
                print(f"  • Rows: {len(df)}")
                print(f"  • Columns: {list(df.columns)}")
                
                if 'mission' in df.columns:
                    print(f"  • Mission breakdown:")
                    for mission, count in df['mission'].value_counts().items():
                        print(f"    - {mission}: {count}")
                
                print(f"\n  First 3 rows:")
                print(df.head(3).to_string(index=False))
            else:
                print(f"\n{name}: ⚠ File not found at {filepath}")
        
        print("\n" + "-" * 70)
        print("\n✅ PIPELINE COMPLETE! Your data is ready for ML training.")
        print("\n📁 Next steps:")
        print("   1. Use all_candidates_standard.csv for training (positive class)")
        print("   2. Use all_false_positives_standard.csv for training (negative class)")
        print("   3. Build your CNN/GBM model")
        print("   4. Create visualizations with SHAP")
        print("   5. Build the dashboard")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating summary: {e}")
        return False

if __name__ == '__main__':
    success = run_pipeline()
    
    if success:
        print("\n" + "="*70)
        print("  🎉 SUCCESS! Ready for NASA Space Apps Challenge! 🎉")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("  ⚠ PIPELINE INCOMPLETE - Check errors above")
        print("="*70 + "\n")
        sys.exit(1)
