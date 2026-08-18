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

## Example Scripts

The `examples/` folder contains ready-to-use scripts demonstrating the library:

### 1. Basic Analysis (`basic_analysis.py`)

Simple usage example showing how to load data, extract parameters, and create plots:

```bash
python examples/basic_analysis.py
```

Demonstrates:
- Loading data from a folder
- Extracting all parameters
- Creating 2x2 plot grid with trends

### 2. Batch Processing (`batch_analysis.py`)

Process multiple measurement folders and export results to CSV:

```bash
python examples/batch_analysis.py
```

Processes all `measurement_*` folders in the current directory and exports parameter tables.

### 3. Custom Analysis (`custom_analysis.py`)

Detailed analysis of a single measurement file using individual extraction methods:

```bash
python examples/custom_analysis.py measurement_step_1.csv
```

Shows:
- Different threshold extraction methods
- Detailed efficiency analysis
- Semi-log I-V for ideality factor
- 2x2 plot comparison

## Usage Examples

### Example 1: Load and Plot Data

```python
from step_stress_analysis import load_folder_data
import matplotlib.pyplot as plt

# Load data
results = load_folder_data("./measurement_data")

# Create a simple plot
fig, ax = plt.subplots()
for ivl in results.ivl_data:
    ax.plot(ivl.current * 1e3, ivl.optical_power * 1e6, 
           label=f"Step {ivl.step}")
ax.set_xlabel("Current (mA)")
ax.set_ylabel("Optical Power (μW)")
ax.legend()
plt.show()
```

### Example 2: Use Visualization Module

```python
from step_stress_analysis import load_folder_data, extract_all_parameters
from step_stress_analysis.visualization import plot_ivl_characteristics
import matplotlib.pyplot as plt

# Load and extract
results = load_folder_data("./measurement_data")
for ivl in results.ivl_data:
    results.parameters.append(extract_all_parameters(ivl))

# Create publication-ready plot
fig = plt.figure(figsize=(12, 10))
plot_ivl_characteristics(fig, results.ivl_data, results.parameters)
plt.savefig("ivl_characteristics.png", dpi=300)
plt.show()
```

### Example 3: Custom Parameter Extraction

```python
from step_stress_analysis import (
    load_measurement_csv,
    extract_threshold_max_slope,
    calculate_power_conversion_efficiency
)

# Load single measurement
ivl = load_measurement_csv("measurement_step_01.csv")

# Extract threshold using maximum slope method
i_th, v_th, _, _ = extract_threshold_max_slope(
    ivl.current, 
    ivl.optical_power
)

# Calculate efficiency
pce_percent = calculate_power_conversion_efficiency(
    ivl.voltage,
    ivl.current,
    ivl.optical_power
)

print(f"Threshold: {i_th*1e3:.4f} mA")
if isinstance(pce_percent, tuple):
    max_pce, _, _ = pce_percent
    print(f"Max PCE: {max_pce:.2f}%")
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
│   ├── visualization.py         # Plotting functions for programmatic use
│   └── gui.py                   # PyQt5 GUI implementation
├── examples/
│   ├── basic_analysis.py        # Minimal usage example with plots
│   ├── batch_analysis.py        # Batch processing multiple datasets
│   └── custom_analysis.py       # Custom parameter extraction methods
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

### Visualization (`visualization.py`)

Reusable plotting functions for programmatic use:

- `plot_ivl_characteristics()`: I-V, L-I, L-V, and semi-log plots
- `plot_stress_monitoring()`: Continuous stress vs. time
- `plot_parameter_trends()`: Parameter degradation trends
- `plot_pce_analysis()`: Power conversion efficiency analysis
- `plot_relative_stress()`: Normalized stress data per step
- `plot_fitting_examples()`: Threshold extraction visualization

All plotting functions work with matplotlib Figures for easy integration into reports or custom workflows.

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
