#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic example: Load and analyze step stress measurement data.

This example shows how to use the step_stress_analysis library
to analyze measurement data without the GUI.

Author: Veronica GaoZhan
Date: February 2026
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Import the library
from step_stress_analysis import (
    load_folder_data,
    extract_all_parameters,
)


def main():
    """Run basic analysis on measurement data."""
    
    # Example: Load data from a folder
    data_folder = Path("example_data")
    
    if not data_folder.exists():
        print(f"Error: Data folder '{data_folder}' not found.")
        print("Please provide a valid measurement folder path.")
        return
    
    print(f"Loading data from: {data_folder}")
    results = load_folder_data(str(data_folder))
    
    print(f"\nLoaded {len(results.ivl_data)} IVL measurements")
    print(f"Loaded {len(results.stress_data)} stress records")
    
    # Extract parameters from each measurement
    print("\nExtracting parameters...")
    for ivl in results.ivl_data:
        param = extract_all_parameters(ivl)
        results.parameters.append(param)
        
        print(f"  Step {param.step}:")
        print(f"    Threshold: {param.threshold_current_A*1e3:.3f} mA @ {param.threshold_voltage_V:.3f} V")
        print(f"    Slope Efficiency: {param.slope_efficiency_W_A*1e3:.3f} mW/A")
        print(f"    Max Power: {param.max_power_W*1e6:.3f} μW")
        print(f"    Max PCE: {param.max_pce_pct:.2f}%")
    
    # Create a simple plot
    print("\nGenerating plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: I-V characteristics
    for i, ivl in enumerate(results.ivl_data):
        axes[0, 0].plot(ivl.voltage, ivl.current * 1e3, label=f"Step {ivl.step}")
    axes[0, 0].set_xlabel("Voltage (V)")
    axes[0, 0].set_ylabel("Current (mA)")
    axes[0, 0].set_title("I-V Characteristics")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: L-I characteristics
    for i, ivl in enumerate(results.ivl_data):
        axes[0, 1].plot(ivl.current * 1e3, ivl.optical_power * 1e6, label=f"Step {ivl.step}")
    axes[0, 1].set_xlabel("Current (mA)")
    axes[0, 1].set_ylabel("Optical Power (μW)")
    axes[0, 1].set_title("L-I Characteristics")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Threshold current trend
    steps = [p.step for p in results.parameters]
    thresholds = [p.threshold_current_A * 1e3 if p.threshold_current_A else 0 for p in results.parameters]
    axes[1, 0].plot(steps, thresholds, 'o-', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel("Step")
    axes[1, 0].set_ylabel("Threshold Current (mA)")
    axes[1, 0].set_title("Threshold Current Degradation")
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Max power trend
    max_powers = [p.max_power_W * 1e6 if p.max_power_W else 0 for p in results.parameters]
    axes[1, 1].plot(steps, max_powers, 's-', linewidth=2, markersize=8, color='tab:orange')
    axes[1, 1].set_xlabel("Step")
    axes[1, 1].set_ylabel("Max Power (μW)")
    axes[1, 1].set_title("Maximum Power vs Stress Step")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
