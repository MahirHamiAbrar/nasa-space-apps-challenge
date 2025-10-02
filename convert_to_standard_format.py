# convert_to_standard_format.py
"""
Convert downloaded NASA Exoplanet Archive data to standardized format.
"""
import pandas as pd
import os

def convert_kepler_to_standard(input_file, output_file):
    """
    Convert Kepler data to standard format.
    
    Kepler column mappings:
    - kepoi_name -> object_name (e.g., "119.01")
    - koi_disposition -> disposition
    - koi_period -> period
    - koi_prad -> planet_radius (Earth radii)
    - koi_steff -> star_temp (Kelvin)
    - koi_srad -> star_radius (Solar radii)
    - koi_smass -> star_mass (Solar masses)
    """
    print(f"\n{'='*60}")
    print(f"Converting Kepler data: {input_file}")
    print(f"{'='*60}")
    
    # Read the data
    df = pd.read_csv(input_file)
    print(f"Original columns: {list(df.columns)}")
    print(f"Original rows: {len(df)}")
    
    # Create standardized dataframe
    standard_df = pd.DataFrame({
        'mission': 'Kepler',
        'object_name': df['kepoi_name'],
        'disposition': df['koi_disposition'],
        'period': df['koi_period'],
        'planet_radius': df['koi_prad'],
        'star_temp': df['koi_steff'],
        'star_radius': df['koi_srad'],
        'star_mass': df['koi_smass'],
        'discovery_facility': 'Kepler'
    })
    
    # Save
    standard_df.to_csv(output_file, index=False)
    print(f"✓ Converted data saved to: {output_file}")
    print(f"✓ Rows: {len(standard_df)}")
    print(f"\nSample data:")
    print(standard_df.head())
    
    return standard_df

def convert_tess_to_standard(input_file, output_file):
    """
    Convert TESS data to standard format.
    
    TESS column mappings:
    - toi -> object_name (e.g., "119.01")
    - tfopwg_disp -> disposition
    - pl_orbper -> period
    - pl_rade -> planet_radius (Earth radii)
    - st_teff -> star_temp (Kelvin)
    - st_rad -> star_radius (Solar radii)
    - st_mass -> star_mass (Solar masses)
    """
    print(f"\n{'='*60}")
    print(f"Converting TESS data: {input_file}")
    print(f"{'='*60}")
    
    # Read the data
    df = pd.read_csv(input_file)
    print(f"Original columns: {list(df.columns)}")
    print(f"Original rows: {len(df)}")
    
    # Map disposition codes to readable names
    disposition_map = {
        'CP': 'CANDIDATE',
        'FP': 'FALSE POSITIVE',
        'PC': 'CANDIDATE',
        'APC': 'CANDIDATE',
        'KP': 'CONFIRMED'
    }
    
    # Create standardized dataframe
    standard_df = pd.DataFrame({
        'mission': 'TESS',
        'object_name': df['toi'].astype(str),
        'disposition': df['tfopwg_disp'].map(disposition_map).fillna(df['tfopwg_disp']),
        'period': df['pl_orbper'] if 'pl_orbper' in df.columns else pd.NA,
        'planet_radius': df['pl_rade'] if 'pl_rade' in df.columns else pd.NA,
        'star_temp': df['st_teff'] if 'st_teff' in df.columns else pd.NA,
        'star_radius': df['st_rad'] if 'st_rad' in df.columns else pd.NA,
        'star_mass': df['st_mass'] if 'st_mass' in df.columns else pd.NA,
        'discovery_facility': 'TESS'
    })
    
    # Save
    standard_df.to_csv(output_file, index=False)
    print(f"✓ Converted data saved to: {output_file}")
    print(f"✓ Rows: {len(standard_df)}")
    print(f"\nSample data:")
    print(standard_df.head())
    
    return standard_df

def convert_k2_to_standard(input_file, output_file):
    """
    Convert K2 data to standard format.
    
    K2 column mappings:
    - epic_name -> object_name
    - k2c_disp -> disposition
    - pl_orbper -> period
    - pl_rade -> planet_radius (Earth radii)
    - st_teff -> star_temp (Kelvin)
    - st_rad -> star_radius (Solar radii)
    - st_mass -> star_mass (Solar masses)
    """
    print(f"\n{'='*60}")
    print(f"Converting K2 data: {input_file}")
    print(f"{'='*60}")
    
    # Read the data
    df = pd.read_csv(input_file)
    print(f"Original columns: {list(df.columns)}")
    print(f"Original rows: {len(df)}")
    
    # Create standardized dataframe
    standard_df = pd.DataFrame({
        'mission': 'K2',
        'object_name': df['epic_name'] if 'epic_name' in df.columns else df['epic_candname'],
        'disposition': df['k2c_disp'],
        'period': df['pl_orbper'] if 'pl_orbper' in df.columns else pd.NA,
        'planet_radius': df['pl_rade'] if 'pl_rade' in df.columns else pd.NA,
        'star_temp': df['st_teff'] if 'st_teff' in df.columns else pd.NA,
        'star_radius': df['st_rad'] if 'st_rad' in df.columns else pd.NA,
        'star_mass': df['st_mass'] if 'st_mass' in df.columns else pd.NA,
        'discovery_facility': 'K2'
    })
    
    # Save
    standard_df.to_csv(output_file, index=False)
    print(f"✓ Converted data saved to: {output_file}")
    print(f"✓ Rows: {len(standard_df)}")
    print(f"\nSample data:")
    print(standard_df.head())
    
    return standard_df

def combine_all_data(input_files, output_file):
    """
    Combine multiple standardized CSV files into one.
    """
    print(f"\n{'='*60}")
    print(f"Combining all data into: {output_file}")
    print(f"{'='*60}")
    
    all_data = []
    
    for file in input_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            all_data.append(df)
            print(f"✓ Loaded {file}: {len(df)} rows")
        else:
            print(f"⚠ File not found: {file}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Combined data saved to: {output_file}")
        print(f"✓ Total rows: {len(combined_df)}")
        print(f"\nDisposition counts:")
        print(combined_df['disposition'].value_counts())
        print(f"\nMission counts:")
        print(combined_df['mission'].value_counts())
        
        return combined_df
    else:
        print("✗ No data to combine!")
        return None


def run_main():
    print("\n" + "="*60)
    print("EXOPLANET DATA FORMAT CONVERTER")
    print("="*60)
    
    data_folder = 'data'
    
    # Convert Kepler candidates
    print("\n[1/6] Converting Kepler candidates...")
    try:
        convert_kepler_to_standard(
            f'{data_folder}/kepler_candidates.csv',
            f'{data_folder}/kepler_candidates_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Convert Kepler false positives
    print("\n[2/6] Converting Kepler false positives...")
    try:
        convert_kepler_to_standard(
            f'{data_folder}/kepler_false_positives.csv',
            f'{data_folder}/kepler_false_positives_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Convert TESS candidates
    print("\n[3/6] Converting TESS candidates...")
    try:
        convert_tess_to_standard(
            f'{data_folder}/tess_candidates.csv',
            f'{data_folder}/tess_candidates_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Convert TESS false positives
    print("\n[4/6] Converting TESS false positives...")
    try:
        convert_tess_to_standard(
            f'{data_folder}/tess_false_positives.csv',
            f'{data_folder}/tess_false_positives_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Combine all candidates
    print("\n[5/6] Combining all candidates...")
    try:
        combine_all_data(
            [
                f'{data_folder}/kepler_candidates_standard.csv',
                f'{data_folder}/tess_candidates_standard.csv',
                f'{data_folder}/k2_candidates_standard.csv',
            ],
            f'{data_folder}/all_candidates_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Combine all false positives
    print("\n[6/6] Combining all false positives...")
    try:
        combine_all_data(
            [
                f'{data_folder}/kepler_false_positives_standard.csv',
                f'{data_folder}/tess_false_positives_standard.csv',
                f'{data_folder}/k2_false_positives_standard.csv',
            ],
            f'{data_folder}/all_false_positives_standard.csv'
        )
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("CONVERSION COMPLETE!")
    print("="*60)
    print("\nStandardized files created:")
    print("  • *_standard.csv - Individual mission data in standard format")
    print("  • all_candidates_standard.csv - All candidates combined")
    print("  • all_false_positives_standard.csv - All false positives combined")
    print("="*60 + "\n")

if __name__ == '__main__':
    run_main()
