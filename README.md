# 🪐 NASA Exoplanet Archive Data Pipeline

A Python-based data pipeline for downloading and processing exoplanet data from NASA's Exoplanet Archive. This project fetches candidate exoplanets and false positives from multiple space missions (Kepler, TESS, K2) and converts them into a standardized format ready for machine learning applications.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Data Source](#data-source)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Output Files](#output-files)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

This pipeline automates the process of:
1. **Querying** NASA's Exoplanet Archive using the TAP (Table Access Protocol) service
2. **Downloading** exoplanet candidate and false positive data
3. **Standardizing** data format across different missions
4. **Combining** datasets into unified CSV files

Originally developed for the **NASA Space Apps Challenge**, this tool provides clean, structured data for training machine learning models to detect exoplanets.

---

## ✨ Features

- ✅ **Multi-Mission Support**: Downloads data from Kepler, TESS, and K2 missions
- ✅ **Automated Pipeline**: One command to download and process all data
- ✅ **TAP Service Integration**: Uses NASA's official Table Access Protocol
- ✅ **Standardized Format**: Converts diverse data sources to unified schema
- ✅ **Separate Classes**: Downloads candidates and false positives independently
- ✅ **Batch Processing**: Efficiently handles large datasets
- ✅ **Error Handling**: Robust error checking and reporting

---

## 🛰️ Data Source

All data is retrieved from the **NASA Exoplanet Archive** using their TAP (Table Access Protocol) service:

- **Base URL**: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- **Protocol**: IVOA Table Access Protocol (TAP)
- **Format**: CSV (Comma-Separated Values)
- **Documentation**: [NASA Exoplanet Archive TAP Guide](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html)

### Data Tables Used

| Table Name | Description | Records |
|------------|-------------|---------|
| `cumulative` | Kepler Objects of Interest (KOI) | ~10,000+ |
| `toi` | TESS Objects of Interest | ~7,000+ |
| `k2pandc` | K2 Planets and Candidates | ~1,000+ |

### Disposition Categories

- **CANDIDATE**: Objects identified as potential exoplanets requiring follow-up
- **FALSE POSITIVE**: Objects determined not to be exoplanets (eclipsing binaries, stellar activity, etc.)
- **CONFIRMED**: Verified exoplanets (not downloaded by default)

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Using `uv` (Recommended)

`uv` is a fast Python package installer and resolver. Install it first if you haven't:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Project Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/exoplanet-data-pipeline.git
cd exoplanet-data-pipeline
```

2. **Create a virtual environment with `uv`:**
```bash
uv venv
```

3. **Activate the virtual environment:**
```bash
# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

4. **Install dependencies with `uv`:**
```bash
uv pip install -r requirements.txt
```

### Manual Installation (without `uv`)

If you prefer using standard `pip`:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencies

Create a `requirements.txt` file with the following:

```text
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

---

## 📁 Project Structure

```
exoplanet-data-pipeline/
│
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore rules
│
├── exoplanet_candidates.py             # Download CANDIDATE data
├── exoplanet_false_positives.py        # Download FALSE POSITIVE data
├── convert_to_standard_format.py       # Convert to standardized format
├── run_all.py                          # Main pipeline executor
│
└── data/                               # Output directory (created on first run)
    ├── kepler_candidates.csv
    ├── kepler_false_positives.csv
    ├── tess_candidates.csv
    ├── tess_false_positives.csv
    ├── k2_candidates.csv
    ├── k2_false_positives.csv
    ├── kepler_candidates_standard.csv
    ├── kepler_false_positives_standard.csv
    ├── tess_candidates_standard.csv
    ├── tess_false_positives_standard.csv
    ├── all_candidates_standard.csv     # Combined candidates
    └── all_false_positives_standard.csv # Combined false positives
```

---

## 🚀 Usage

### Quick Start

Run the complete pipeline with a single command:

```bash
python run_all.py
```

This will:
1. Fetch available tables from NASA Exoplanet Archive
2. Download candidate data from Kepler, TESS, and K2
3. Download false positive data from all missions
4. Convert all data to standardized format
5. Combine datasets into unified files

### Individual Scripts

You can also run each script independently:

#### 1. Download Candidates Only
```bash
python exoplanet_candidates.py
```
**Output:**
- `data/kepler_candidates.csv`
- `data/tess_candidates.csv`
- `data/k2_candidates.csv`

#### 2. Download False Positives Only
```bash
python exoplanet_false_positives.py
```
**Output:**
- `data/kepler_false_positives.csv`
- `data/tess_false_positives.csv`
- `data/k2_false_positives.csv`

#### 3. Convert to Standard Format
```bash
python convert_to_standard_format.py
```
**Output:**
- `data/*_standard.csv` files
- `data/all_candidates_standard.csv`
- `data/all_false_positives_standard.csv`

---

## 📊 Output Files

### Raw Data Files

Downloaded directly from NASA Exoplanet Archive with original column names:

- **Kepler**: `kepoi_name`, `koi_period`, `koi_prad`, `koi_steff`, etc.
- **TESS**: `toi`, `pl_orbper`, `pl_rade`, `st_teff`, etc.
- **K2**: `epic_name`, `pl_orbper`, `pl_rade`, `st_teff`, etc.

### Standardized Format Files

All data converted to a unified schema:

| Column | Type | Description | Units |
|--------|------|-------------|-------|
| `mission` | string | Mission name | Kepler, TESS, K2 |
| `object_name` | string | Unique object identifier | e.g., K00711.03, 5150.01 |
| `disposition` | string | Classification status | CANDIDATE, FALSE POSITIVE |
| `period` | float | Orbital period | days |
| `planet_radius` | float | Planet radius | Earth radii |
| `star_temp` | float | Stellar temperature | Kelvin |
| `star_radius` | float | Stellar radius | Solar radii |
| `star_mass` | float | Stellar mass | Solar masses |
| `discovery_facility` | string | Discovery facility | Mission name or UNKNOWN |

### Example Output

```csv
mission,object_name,disposition,period,planet_radius,star_temp,star_radius,star_mass,discovery_facility
Kepler,K00711.03,CANDIDATE,124.524522,2.690000,5497.000000,1.046000,0.988000,Kepler
TESS,5150.01,FALSE POSITIVE,1.757829,13.943300,6640.000000,2.590000,1.100000,TESS
K2,201367065,CANDIDATE,8.521543,2.100000,5400.000000,0.950000,0.980000,K2
```

---

## 🔧 API Reference

### Core Functions

#### `get_available_tables()`
Fetches list of all available tables from NASA Exoplanet Archive.

```python
from exoplanet_candidates import get_available_tables

tables = get_available_tables()
print(tables)  # ['ps', 'cumulative', 'toi', 'k2pandc', ...]
```

**Returns:** `list[str]` - List of table names

---

#### `construct_tap_url(table, columns, where_clause, order_by, limit)`
Constructs a TAP query URL for downloading data.

```python
from exoplanet_candidates import construct_tap_url

url = construct_tap_url(
    table='cumulative',
    columns='kepoi_name,koi_period,koi_prad',
    where_clause="koi_disposition='CANDIDATE' and koi_period>100",
    order_by='koi_period',
    limit=1000
)
```

**Parameters:**
- `table` (str): Table name (e.g., 'cumulative', 'toi')
- `columns` (str): Comma-separated column names or '*' for all
- `where_clause` (str): SQL WHERE clause (without 'WHERE' keyword)
- `order_by` (str): Column name to sort by
- `limit` (int, optional): Maximum rows to return

**Returns:** `str` - Complete TAP query URL

---

#### `download_data(table, folder, columns, where_clause, order_by, filename)`
Downloads data from specified table and saves to CSV.

```python
from exoplanet_candidates import download_data

download_data(
    table='cumulative',
    folder='data',
    where_clause="koi_disposition='CANDIDATE'",
    order_by='kepoi_name',
    filename='kepler_candidates.csv'
)
```

**Parameters:**
- `table` (str): Table to query
- `folder` (str): Output directory path
- `columns` (str): Columns to select (default: '*')
- `where_clause` (str): Filter condition
- `order_by` (str): Sort column
- `filename` (str): Output filename

**Returns:** `str` - Path to saved file

---

### Conversion Functions

#### `convert_kepler_to_standard(input_file, output_file)`
Converts Kepler data to standardized format.

**Column Mapping:**
- `kepoi_name` → `object_name`
- `koi_disposition` → `disposition`
- `koi_period` → `period`
- `koi_prad` → `planet_radius`
- `koi_steff` → `star_temp`
- `koi_srad` → `star_radius`
- `koi_smass` → `star_mass`

#### `convert_tess_to_standard(input_file, output_file)`
Converts TESS data to standardized format.

**Disposition Mapping:**
- `CP` → `CANDIDATE`
- `FP` → `FALSE POSITIVE`
- `PC` → `CANDIDATE`

#### `combine_all_data(input_files, output_file)`
Combines multiple standardized CSV files into one.

---

## 📈 Data Statistics

Typical dataset sizes (as of 2024):

| Mission | Candidates | False Positives |
|---------|-----------|-----------------|
| Kepler | ~2,000 | ~5,000 |
| TESS | ~4,000 | ~2,000 |
| K2 | ~500 | ~300 |
| **Total** | **~6,500** | **~7,300** |

---

## 🐛 Troubleshooting

### Empty CSV Files

**Problem:** Downloaded files are empty or have no data rows.

**Solutions:**
- Check WHERE clause syntax - values are case-sensitive!
  - Use `'CANDIDATE'` not `'candidate'`
  - Use `'FALSE POSITIVE'` not `'False Positive'`
- Verify table name spelling
- Check internet connection

### Connection Timeout

**Problem:** `requests.exceptions.Timeout`

**Solutions:**
- Increase timeout in script (default: 120 seconds)
- Check NASA Exoplanet Archive status
- Try again later

### Missing Columns

**Problem:** `KeyError` when converting to standard format

**Solutions:**
- Some missions may not have all columns (e.g., star_mass)
- Missing values are filled with median or NaN
- Check original data columns with `pandas.read_csv(file).columns`

---

## 🔍 Advanced Usage

### Custom Queries

Download specific subsets of data:

```python
from exoplanet_candidates import download_data

# Small planets around Sun-like stars
download_data(
    table='cumulative',
    where_clause="koi_disposition='CANDIDATE' and koi_prad<2 and koi_steff>5000 and koi_steff<6000",
    filename='earth_like_candidates.csv'
)

# Long-period candidates
download_data(
    table='toi',
    where_clause="tfopwg_disp='CP' and pl_orbper>100",
    filename='long_period_tess.csv'
)
```

### Query TAP Schema

Explore available columns:

```python
from exoplanet_candidates import construct_tap_url, download_data

# Get all columns for cumulative table
download_data(
    table='TAP_SCHEMA.columns',
    where_clause="table_name='cumulative'",
    filename='cumulative_columns.csv'
)
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📚 Resources

- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)
- [TAP Service Documentation](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html)
- [Column Definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html)
- [IVOA TAP Standard](http://www.ivoa.net/documents/TAP/)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- NASA Exoplanet Science Institute for providing the data
- Kepler, TESS, and K2 mission teams
- NASA Space Apps Challenge community

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the NASA Space Apps Challenge** 🚀🪐