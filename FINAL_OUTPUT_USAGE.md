# Final Output Generator - Usage Guide

## Overview

This script takes your model's predictions and combines them with the actual exoplanet data to generate a final output CSV that includes all object details with predicted dispositions.

## Input Format

### Prediction File (CSV)
Your model should output a CSV with this format:

```csv
object_name,predicted_probability
119.01,0.855043
119.02,0.851574
121.01,0.202328
124.01,0.034818
125.04,0.925812
```

**Columns:**
- `object_name`: Object identifier (e.g., "119.01", "K00711.03")
- `predicted_probability`: Probability that object is a real exoplanet (0.0 to 1.0)

## Output Format

The script generates a CSV with complete object information:

```csv
mission,object_name,disposition,period,planet_radius,star_temp,star_radius,star_mass,discovery_facility
Kepler,K00711.03,CONFIRMED,124.524522,2.690000,5497.000000,1.046000,0.988000,Kepler
TESS,5150.01,FALSE POSITIVE,1.757829,13.943300,6640.000000,2.590000,1.100000,TESS
ARCHIVE,PLANET_168,CONFIRMED,300.262512,13.237900,9170.291947,3.498023,2.619901,UNKNOWN
```

## Usage

### Basic Usage

```bash
python generate_final_output.py predictions.csv
```

This uses default paths:
- Candidates: `data/all_candidates_standard.csv`
- False Positives: `data/all_false_positives_standard.csv`
- Output: `data/final_output.csv`
- Threshold: `0.5`

### Custom Paths

```bash
python generate_final_output.py predictions.csv \
    --candidates data/all_candidates_standard.csv \
    --false-positives data/all_false_positives_standard.csv \
    --output results/final_predictions.csv \
    --threshold 0.6
```

### Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `prediction_file` | - | Path to predictions CSV (required) | - |
| `--candidates` | `-c` | Path to candidates data | `data/all_candidates_standard.csv` |
| `--false-positives` | `-f` | Path to false positives data | `data/all_false_positives_standard.csv` |
| `--output` | `-o` | Output file path | `data/final_output.csv` |
| `--threshold` | `-t` | Probability threshold for CONFIRMED | `0.5` |

### Threshold Explanation

The threshold determines how predictions are classified:

- **`predicted_probability >= threshold`** → `CONFIRMED` (Real exoplanet)
- **`predicted_probability < threshold`** → `FALSE POSITIVE` (Not an exoplanet)

**Examples:**
- `threshold=0.5` (default): Standard 50% confidence
- `threshold=0.7`: More conservative (fewer false positives)
- `threshold=0.3`: More permissive (fewer missed detections)

## How It Works

### Step 1: Load Predictions
Reads your predictions CSV and validates format.

### Step 2: Load Standard Data
Loads both candidates and false positives from standard format files.

### Step 3: Match Objects
Matches prediction object names with actual data using intelligent name normalization:

**Supported Name Formats:**
- `119.01` ↔ `119.01`
- `K00711.03` ↔ `711.03`
- `KOI-711.03` ↔ `711.03`
- `TOI 119.01` ↔ `119.01`
- `EPIC 201367065` ↔ `201367065`

### Step 4: Assign Disposition
Uses the threshold to classify objects:
```python
if predicted_probability >= threshold:
    disposition = "CONFIRMED"
else:
    disposition = "FALSE POSITIVE"
```

### Step 5: Handle Unmatched
Objects in predictions but not in standard data get special treatment:
- Assigned to mission: `ARCHIVE`
- Object name: `PLANET_<index>`
- Discovery facility: `UNKNOWN`
- Missing data fields: `NaN`

### Step 6: Generate Output
Creates final CSV with complete information.

## Example Workflow

### 1. Train Your Model
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load training data
train = pd.read_csv('data/ml_dataset_train.csv')
X = train[['period', 'planet_radius', 'star_temp', 'star_radius', 'star_mass']]
y = (train['disposition'] == 'CONFIRMED').astype(int)

# Train model
model = RandomForestClassifier()
model.fit(X, y)
```

### 2. Make Predictions
```python
# Load test data
test = pd.read_csv('data/ml_dataset_test.csv')
X_test = test[['period', 'planet_radius', 'star_temp', 'star_radius', 'star_mass']]

# Predict probabilities
probabilities = model.predict_proba(X_test)[:, 1]

# Create predictions dataframe
predictions = pd.DataFrame({
    'object_name': test['object_name'],
    'predicted_probability': probabilities
})

# Save predictions
predictions.to_csv('predictions.csv', index=False)
```

### 3. Generate Final Output
```bash
python generate_final_output.py predictions.csv --output final_results.csv
```

### 4. Review Results
```python
import pandas as pd

results = pd.read_csv('final_results.csv')
print(results.head(10))

# Check distribution
print(results['disposition'].value_counts())
```

## Output Statistics

The script automatically prints statistics:

```
FINAL OUTPUT STATISTICS
======================================================================

Total objects: 1000

Disposition Distribution:
  • CONFIRMED: 450 (45.0%)
  • FALSE POSITIVE: 550 (55.0%)

Mission Distribution:
  • Kepler: 600 (60.0%)
  • TESS: 350 (35.0%)
  • ARCHIVE: 50 (5.0%)

Data Completeness:
  • period: 950/1000 (95.0%)
  • planet_radius: 920/1000 (92.0%)
  • star_temp: 880/1000 (88.0%)
  • star_radius: 870/1000 (87.0%)
  • star_mass: 850/1000 (85.0%)
```

## Common Issues

### Issue: "No matching data found"
**Cause:** Object names in predictions don't match standard data.

**Solutions:**
1. Check object name format in predictions
2. Verify standard data files exist
3. Check for typos in object names

### Issue: "All objects assigned to ARCHIVE"
**Cause:** Name normalization failing to match.

**Solutions:**
1. Ensure object names follow standard format
2. Check that standard data files contain the expected objects
3. Manually verify object name formats

### Issue: Wrong disposition counts
**Cause:** Threshold too high or too low.

**Solutions:**
1. Adjust threshold with `--threshold` flag
2. Review model calibration
3. Check prediction probabilities distribution

## Best Practices

1. **Always validate predictions format:**
   ```python
   preds = pd.read_csv('predictions.csv')
   assert 'object_name' in preds.columns
   assert 'predicted_probability' in preds.columns
   assert preds['predicted_probability'].between(0, 1).all()
   ```

2. **Choose appropriate threshold:**
   - Use validation set to optimize threshold
   - Consider cost of false positives vs false negatives
   - Default 0.5 is a good starting point

3. **Keep standard data updated:**
   - Re-run data download pipeline periodically
   - NASA adds new candidates regularly

4. **Backup output files:**
   ```bash
   cp final_output.csv final_output_$(date +%Y%m%d).csv
   ```

## Integration with Dashboard

After generating final output, use it for visualization:

```python
import pandas as pd
import plotly.express as px

# Load results
results = pd.read_csv('data/final_output.csv')

# Create interactive plot
fig = px.scatter(
    results,
    x='period',
    y='planet_radius',
    color='disposition',
    hover_data=['object_name', 'mission', 'star_temp'],
    title='Exoplanet Predictions'
)
fig.show()
```

## Next Steps

1. ✅ Generate predictions from your model
2. ✅ Run this script to create final output
3. ✅ Analyze results and statistics
4. ✅ Create visualizations (scatter plots, histograms)
5. ✅ Generate SHAP explanations for predictions
6. ✅ Build interactive dashboard

---

**Questions?** Check the main README or open an issue on GitHub.