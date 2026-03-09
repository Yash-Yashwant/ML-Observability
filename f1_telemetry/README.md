# F1 Telemetry Dashboard

Real-time F1 telemetry visualization and analytics platform with Bayesian predictive models.

## Features

### Core Features
- Live telemetry replay from archived data
- Real-time position tracking and visualization
- Bayesian tire degradation prediction
- Sector-by-sector performance analysis
- Lap time prediction with confidence intervals
- Strategy optimization recommendations

### Advanced Analytics
- Tire compound performance modeling
- Fuel load effect compensation
- Track condition adaptation
- Traffic impact analysis
- Optimal pit window prediction

## Architecture

```
data/
├── raw/              # Raw telemetry data (output.json)
├── processed/        # Preprocessed dataframes
└── cache/            # FastF1 cache

src/
├── preprocessing/    # Data decompression & parsing
├── models/          # Bayesian statistical models
├── replay/          # Replay engine
├── visualization/   # Dashboard UI
└── analytics/       # Advanced metrics

notebooks/           # Exploratory analysis
tests/              # Unit tests
```

## Technology Stack

- **Data Processing**: pandas, numpy, zlib
- **Statistical Models**: PyMC (Bayesian inference)
- **Visualization**: Plotly Dash / Streamlit
- **Performance**: Polars (for large datasets)
- **Testing**: pytest

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Process raw telemetry
python -m src.preprocessing.parse_telemetry --input data/raw/output.json

# Start dashboard
python -m src.dashboard.app --session "2026-Australian-GP-Qualifying"
```
