#!/usr/bin/env python3
"""
Generate final output CSV combining predictions with actual data.
Takes prediction CSV and merges with standard format data to create final output.
"""
import pandas as pd
import numpy as np
import os
import argparse

def load_predictions(prediction_file):
    """
    Load predictions from CSV file.
    
    Expected format:
    object_name,predicted_probability
    119.01,0.855043
    """
    print(f"\n📂 Loading predictions from: {prediction_file}")
    
    if not os.path.exists(prediction_file):
        raise FileNotFoundError(f"Prediction file not found: {prediction_file}")
    
    predictions = pd.read_csv(prediction_file)
    
    # Validate columns
    required_cols = ['object_name', 'predicted_probability']
    missing_cols = set(required_cols) - set(predictions.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    print(f"✓ Loaded {len(predictions)} predictions")
    print(f"  Columns: {list(predictions.columns)}")
    
    return predictions

def load_standard_data(candidates_file, false_positives_file):
    """
    Load standard format candidate and false positive data.
    """
    print("\n📂 Loading standard format data...")
    
    # Load candidates
    if os.path.exists(candidates_file):
        candidates = pd.read_csv(candidates_file)
        print(f"✓ Loaded {len(candidates)} candidates from {candidates_file}")
    else:
        print(f"⚠ Candidates file not found: {candidates_file}")
        candidates = pd.DataFrame()
    
    # Load false positives
    if os.path.exists(false_positives_file):
        false_positives = pd.read_csv(false_positives_file)
        print(f"✓ Loaded {len(false_positives)} false positives from {false_positives_file}")
    else:
        print(f"⚠ False positives file not found: {false_positives_file}")
        false_positives = pd.DataFrame()
    
    # Combine
    all_data = pd.concat([candidates, false_positives], ignore_index=True)
    print(f"✓ Combined total: {len(all_data)} objects")
    
    return all_data

def normalize_object_name(name):
    """
    Normalize object names for matching.
    Handles various formats:
    - K00711.03 -> 711.03
    - 119.01 -> 119.01
    - EPIC 201367065 -> 201367065
    """
    if pd.isna(name):
        return ''
    
    name = str(name).strip()
    
    # Remove common prefixes
    prefixes = ['K', 'KOI-', 'KOI ', 'TOI-', 'TOI ', 'EPIC ', 'EPIC-']
    for prefix in prefixes:
        if name.upper().startswith(prefix.upper()):
            name = name[len(prefix):]
            break
    
    # Remove leading zeros from the first part before decimal
    if '.' in name:
        parts = name.split('.')
        parts[0] = str(int(parts[0])) if parts[0].isdigit() else parts[0]
        name = '.'.join(parts)
    
    return name.strip()

def match_predictions_with_data(predictions, all_data, threshold=0.5):
    """
    Match predictions with actual data and assign final disposition.
    
    Args:
        predictions: DataFrame with object_name and predicted_probability
        all_data: DataFrame with standard format data
        threshold: Probability threshold for CONFIRMED classification
    
    Returns:
        DataFrame with final output format
    """
    print("\n🔗 Matching predictions with data...")
    print(f"  Threshold for CONFIRMED: {threshold}")
    
    # Normalize object names in both datasets
    predictions['normalized_name'] = predictions['object_name'].apply(normalize_object_name)
    all_data['normalized_name'] = all_data['object_name'].apply(normalize_object_name)
    
    # Create a lookup dictionary for faster matching
    data_lookup = {}
    for idx, row in all_data.iterrows():
        norm_name = row['normalized_name']
        if norm_name and norm_name not in data_lookup:
            data_lookup[norm_name] = row.to_dict()
    
    print(f"  Created lookup for {len(data_lookup)} unique objects")
    
    # Match predictions with data
    matched_data = []
    unmatched = []
    
    for idx, pred_row in predictions.iterrows():
        norm_name = pred_row['normalized_name']
        prob = pred_row['predicted_probability']
        
        # Determine disposition based on probability
        predicted_disposition = 'CONFIRMED' if prob >= threshold else 'FALSE POSITIVE'
        
        # Try to find matching data
        if norm_name in data_lookup:
            data_row = data_lookup[norm_name].copy()
            # Override disposition with prediction
            data_row['disposition'] = predicted_disposition
            matched_data.append(data_row)
        else:
            # Create entry for unmatched prediction
            unmatched.append(pred_row['object_name'])
            matched_data.append({
                'mission': 'ARCHIVE',
                'object_name': f"PLANET_{idx}",
                'disposition': predicted_disposition,
                'period': np.nan,
                'planet_radius': np.nan,
                'star_temp': np.nan,
                'star_radius': np.nan,
                'star_mass': np.nan,
                'discovery_facility': 'UNKNOWN'
            })
    
    # Create final dataframe
    final_df = pd.DataFrame(matched_data)
    
    # Ensure proper column order
    column_order = [
        'mission', 'object_name', 'disposition', 'period',
        'planet_radius', 'star_temp', 'star_radius', 'star_mass',
        'discovery_facility'
    ]
    final_df = final_df[column_order]
    
    print(f"✓ Matched {len(matched_data)} predictions")
    if unmatched:
        print(f"⚠ {len(unmatched)} predictions had no matching data (created ARCHIVE entries)")
        if len(unmatched) <= 10:
            print(f"  Unmatched: {unmatched}")
    
    return final_df

def add_statistics(df):
    """
    Print statistics about the final dataset.
    """
    print("\n" + "="*70)
    print("FINAL OUTPUT STATISTICS")
    print("="*70)
    
    print(f"\nTotal objects: {len(df)}")
    
    print("\nDisposition Distribution:")
    for disp, count in df['disposition'].value_counts().items():
        print(f"  • {disp}: {count} ({count/len(df)*100:.1f}%)")
    
    print("\nMission Distribution:")
    for mission, count in df['mission'].value_counts().items():
        print(f"  • {mission}: {count} ({count/len(df)*100:.1f}%)")
    
    print("\nData Completeness:")
    for col in ['period', 'planet_radius', 'star_temp', 'star_radius', 'star_mass']:
        non_null = df[col].notna().sum()
        print(f"  • {col}: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}%)")

def save_output(df, output_file):
    """
    Save final output to CSV file.
    """
    print(f"\n💾 Saving final output to: {output_file}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"✓ Saved {len(df)} objects")
    
    # Show preview
    print(f"\n📊 Preview of output (first 10 rows):")
    print(df.head(10).to_string(index=True))

def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(
        description='Generate final output CSV from predictions and standard data'
    )
    parser.add_argument(
        'prediction_file',
        help='Path to prediction CSV file (object_name, predicted_probability)'
    )
    parser.add_argument(
        '-c', '--candidates',
        default='data/all_candidates_standard.csv',
        help='Path to candidates standard format file (default: data/all_candidates_standard.csv)'
    )
    parser.add_argument(
        '-f', '--false-positives',
        default='data/all_false_positives_standard.csv',
        help='Path to false positives standard format file (default: data/all_false_positives_standard.csv)'
    )
    parser.add_argument(
        '-o', '--output',
        default='data/final_output.csv',
        help='Output CSV file path (default: data/final_output.csv)'
    )
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.5,
        help='Probability threshold for CONFIRMED classification (default: 0.5)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  🔮 FINAL OUTPUT GENERATOR  🔮")
    print("="*70)
    print(f"\nInput files:")
    print(f"  • Predictions: {args.prediction_file}")
    print(f"  • Candidates: {args.candidates}")
    print(f"  • False Positives: {args.false_positives}")
    print(f"\nOutput file: {args.output}")
    print(f"Threshold: {args.threshold}")
    
    try:
        # Step 1: Load predictions
        predictions = load_predictions(args.prediction_file)
        
        # Step 2: Load standard data
        all_data = load_standard_data(args.candidates, args.false_positives)
        
        # Step 3: Match predictions with data
        final_output = match_predictions_with_data(
            predictions, 
            all_data, 
            threshold=args.threshold
        )
        
        # Step 4: Add statistics
        add_statistics(final_output)
        
        # Step 5: Save output
        save_output(final_output, args.output)
        
        print("\n" + "="*70)
        print("  ✅ SUCCESS! Final output generated.  ✅")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
