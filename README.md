# Step Stress Data Analysis Library

A comprehensive Python package for analyzing step stress measurement data from semiconductor devices (VCSELs, laser diodes, and other optoelectronic components).

**Author:** Veronica GaoZhan  
**Date:** February 2026  
**License:** MIT

## Features

- **Complete Data Analysis Pipeline**: Load, process, and analyze step stress measurement data
- **Advanced Parameter Extraction**: Multiple methods for threshold current, slope efficiency, and efficiency parameters
- **Interactive GUI**: PyQt5-based graphical interface for real-time data visualization
- **Programmatic API**: Use the library in your own Python applications
- **Publication-Ready Visualizations**: 6 comprehensive plot categories with matplotlib
- **CSV Export**: Export all extracted parameters to CSV for further analysis
- **Multi-dataset Support**: Analyze single files or entire folders of measurements

## Installation

### From GitHub

```bash
pip install git+https://github.com/vvvvvero/Laser_Optical_Reliablity_Analysis_1_Step_Stress.git
```

### From Source

```bash
git clone https://github.com/vvvvvero/Laser_Optical_Reliablity_Analysis_1_Step_Stress.git
cd step_stress_analysis_lib
pip install -e .
```

## Quick Start

### GUI Application

Launch the interactive analysis GUI:

```bash
python main.py
```

Or after installation:

```bash
step-stress-analysis
```

### Programmatic Usage

```python
from step_stress_analysis import load_folder_data, extract_all_parameters

# Load measurement data from a folder
results = load_folder_data("./measurement_results")

# Extract parameters from each measurement
for ivl in results.ivl_data:
    params = extract_all_parameters(ivl)
    print(f"Step {params.step}: Ith={params.threshold_current_A*1e3:.4f} mA")
```

## Project Structure

```
step_stress_analysis_lib/
├── step_stress_analysis/
│   ├── __init__.py              # Package initialization and public API
│   ├── models.py                # Data classes (IVLData, ExtractedParameters, etc.)
│   ├── data_loader.py           # Functions to load CSV measurement files
│   ├── parameter_extractor.py   # Parameter extraction algorithms
│   ├── analysis_worker.py       # QThread worker for GUI responsiveness
│   └── gui.py                   # PyQt5 GUI implementation
├── examples/
│   └── basic_usage.py           # Example scripts demonstrating the library
├── main.py                      # GUI application entry point
├── setup.py                     # Package configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # MIT License
└── .gitignore                   # Git configuration
```

## Core Components

### Data Models (`models.py`)

- **IVLData**: Stores I-V-Light measurements at a single stress level
- **StressData**: Stores stress monitoring data (voltage, current over time)
- **ExtractedParameters**: Holds all extracted optical and electrical parameters
- **AnalysisResults**: Container for complete analysis results

### Data Loading (`data_loader.py`)

- `load_measurement_csv()`: Load single measurement file
- `load_iv_power_csv()`: Load IV+Power format files
- `load_stress_csv()`: Load stress monitoring data
- `load_folder_data()`: Load entire folder of measurements

### Parameter Extraction (`parameter_extractor.py`)

**Threshold Current Methods:**
- Maximum slope method (dP/dI)
- Second derivative method
- Log-log derivative method
- P/I ratio method
- Noise floor method
- Combined median method

**Optical/Electrical Parameters:**
- Slope efficiency (mW/A)
- Power conversion efficiency (%)
- Maximum optical power
- Rollover characteristics
- Ideality factor (n)
- Series resistance (Ω)
- Wall-plug efficiency

### GUI Features (`gui.py`)

**6 Analysis Tabs:**

1. **IVL Characteristics**: I-V, L-I, L-V, and semi-log plots
2. **Stress Monitoring**: Current and voltage vs. time during stress
3. **Relative Stress**: Normalized stress parameters
4. **Parameter Trends**: How extracted parameters change with stress
5. **Fitting Examples**: Detailed fitting visualizations
6. **PCE Analysis**: Power conversion efficiency analysis

**Export Capabilities:**
- CSV export with 22 parameter columns
- High-resolution matplotlib figures
- Real-time plotting with zoom/pan tools

## Data File Formats

### Measurement Files

CSV format with columns:
```
Step,Stress_Level,Point,Timestamp,Setpoint,Voltage_V,Current_A,Optical_Power_W,Status
```

### Stress Monitoring Files

CSV format with columns:
```
Relative_Time_s,Voltage_V,Current_A,Optical_Power_W
```

## Configuration Parameters

The GUI allows configuration of:

- **Voltage/Current Ranges**: Measurement limits
- **Number of Points**: Data resolution
- **Integration Time**: Measurement duration
- **Stress Parameters**: Duration, level, pulse parameters
- **Output Options**: CSV export paths

## Usage Examples

### Example 1: Basic Analysis

```python
from step_stress_analysis import load_folder_data, extract_all_parameters

# Load data
results = load_folder_data("./measurement_data")

# Process each step
for ivl in results.ivl_data:
    params = extract_all_parameters(ivl)
    print(f"Threshold: {params.threshold_current_A*1e3:.4f} mA")
    print(f"Max Power: {params.max_power_W*1e6:.4f} μW")
    print(f"PCE: {params.max_pce_pct:.2f}%")
```

### Example 2: Custom Analysis

```python
import numpy as np
from step_stress_analysis import (
    load_measurement_csv,
    extract_threshold_max_slope,
    calculate_power_conversion_efficiency
)

# Load single measurement
ivl = load_measurement_csv("measurement_step_01.csv")

# Custom threshold extraction
i_th, slope, i_arr, slope_arr = extract_threshold_max_slope(
    ivl.current, 
    ivl.optical_power
)

# Efficiency analysis
i_pce, pce, max_pce, _, _ = calculate_power_conversion_efficiency(
    ivl.voltage,
    ivl.current,
    ivl.optical_power
)

print(f"Threshold: {i_th*1e3:.4f} mA")
print(f"Max PCE: {max_pce:.2f}%")
```

### Example 3: Batch Processing

```python
from pathlib import Path
import csv
from step_stress_analysis import load_folder_data, extract_all_parameters

# Load all data
results = load_folder_data("./results")

# Export to CSV
with open("analysis_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Step", "Stress", "Ith_mA", "Pmax_uW", "PCE_pct"
    ])
    writer.writeheader()
    
    for p in results.parameters:
        writer.writerow({
            "Step": p.step,
            "Stress": f"{p.stress_level:.6f}",
            "Ith_mA": f"{p.threshold_current_A*1e3:.6f}",
            "Pmax_uW": f"{p.max_power_W*1e6:.6f}",
            "PCE_pct": f"{p.max_pce_pct:.4f}"
        })
```

## Output Files

### Parameter Export CSV

Columns exported:
- Step, Stress_Level
- Threshold_Current_mA, Threshold_Voltage_V, Slope_Efficiency_mW_A
- Rollover_Current_mA, Rollover_Voltage_V, Rollover_Power_uW
- Max_Power_uW, Current_at_Max_Power_mA, Voltage_at_Max_Power_V
- Max_PCE_pct, Current_at_Max_PCE_mA, Voltage_at_Max_PCE_V
- Ideality_Factor, I0_A, Series_Resistance_Ohm, Differential_Resistance_Ohm
- Wall_Plug_Efficiency_pct, Knee_Voltage_V, Fit_Quality_R2

## Requirements

- **Python**: 3.7 or later
- **PyQt5**: 5.15 or later (GUI)
- **NumPy**: 1.19 or later (numerical processing)
- **Matplotlib**: 3.3 or later (plotting)
- **SciPy**: 1.5 or later (optimization, signal processing)

## API Reference

### Main Classes

#### IVLData
```python
@dataclass
class IVLData:
    step: int
    stress_level: float
    voltage: np.ndarray      # Voltage array (V)
    current: np.ndarray      # Current array (A)
    optical_power: np.ndarray  # Optical power (W)
    setpoint: np.ndarray     # Setpoint array
    timestamp: np.ndarray    # Timestamp array (optional)
```

#### ExtractedParameters
```python
@dataclass
class ExtractedParameters:
    step: int
    stress_level: float
    
    # Threshold parameters
    threshold_current_A: Optional[float]
    threshold_voltage_V: Optional[float]
    slope_efficiency_W_A: Optional[float]
    threshold_method: str
    
    # Power parameters
    max_power_W: Optional[float]
    rollover_current_A: Optional[float]
    rollover_voltage_V: Optional[float]
    
    # Efficiency parameters
    max_pce_pct: Optional[float]
    wall_plug_efficiency: Optional[float]
    
    # Electrical parameters
    ideality_factor: Optional[float]
    series_resistance_ohm: Optional[float]
    I0_A: Optional[float]
    # ... and more
```

### Key Functions

#### Data Loading
```python
def load_folder_data(folder_path: str, log_callback=None) -> AnalysisResults
def load_measurement_csv(filepath: str) -> Optional[IVLData]
def load_stress_csv(filepath: str, step: int = 0, stress_level: float = 0.0) -> Optional[StressData]
```

#### Parameter Extraction
```python
def extract_all_parameters(ivl: IVLData) -> ExtractedParameters
def extract_threshold_max_slope(current, power) -> (i_th, slope, i_arr, slope_arr)
def calculate_power_conversion_efficiency(voltage, current, power) -> (i, pce, max_pce, i_max, v_max)
def extract_ideality_factor(voltage, current) -> (n, I0, r2)
def extract_series_resistance(voltage, current) -> (Rs, Rd)
```

## Troubleshooting

### GUI doesn't start
```bash
python -m PyQt5.examples.systray  # Test PyQt5 installation
pip install --upgrade PyQt5
```

### Data not loading
- Ensure CSV files have correct headers
- Check file paths are correct
- Verify data format matches expected columns

### Parameters not extracting
- Ensure sufficient data points (minimum ~10 points)
- Check for valid numerical values
- Verify current and power data are positive

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## Citation

If you use this library in your research, please cite:

```
GaoZhan, V. (2026). Step Stress Data Analysis Library [Computer software].
Retrieved from https://github.com/vvvvvero/Laser_Optical_Reliablity_Analysis_1_Step_Stress
```

## References

- Thermal and optical characterization of VCSELs and laser diodes
- Semiconductor reliability testing and failure analysis
- Power conversion efficiency measurements
- Device parameter extraction methodology

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing documentation
- Review example scripts in `examples/` folder

---

**Created by Veronica GaoZhan**  
