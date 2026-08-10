#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example usage of step_stress_analysis library without GUI.

This demonstrates how to programmatically use the analysis library
for batch processing or integration into other applications.

Author: Veronica GaoZhan
Date: February 2026
"""

from pathlib import Path
import numpy as np
from step_stress_analysis import (
    load_folder_data,
    extract_all_parameters,
    load_measurement_csv,
    calculate_power_conversion_efficiency,
    extract_threshold_max_slope
)


def example_basic_analysis():
    """Example 1: Basic folder analysis with parameter extraction"""
    
    print("=" * 60)
    print("Example 1: Basic Folder Analysis")
    print("=" * 60)
    
    # Specify the folder containing measurement data
    data_folder = Path("./results")  # Change this to your data folder
    
    if not data_folder.exists():
        print(f"Data folder not found: {data_folder}")
        print("Please create a './results' folder with CSV measurement files")
        return
    
    # Load all data from the folder
    print(f"\nLoading data from: {data_folder}")
    results = load_folder_data(str(data_folder))
    
    # Display summary
    print(f"\n✓ Loaded {len(results.ivl_data)} IVL measurements")
    print(f"✓ Loaded {len(results.stress_data)} stress records")
    
    # Extract parameters from each measurement
    print("\nExtracting parameters...")
    for ivl in results.ivl_data:
        params = extract_all_parameters(ivl)
        results.parameters.append(params)
        
        print(f"\nStep {params.step} (Stress: {params.stress_level:.4f}):")
        print(f"  Threshold current:  {params.threshold_current_A*1e3:.4f} mA")
        print(f"  Threshold voltage:  {params.threshold_voltage_V:.4f} V")
        print(f"  Slope efficiency:   {params.slope_efficiency_W_A*1e3:.4f} mW/A")
        print(f"  Max power:          {params.max_power_W*1e6:.4f} μW")
        print(f"  Max PCE:            {params.max_pce_pct:.2f}%")
        print(f"  Ideality factor:    {params.ideality_factor:.4f}" if params.ideality_factor else "  Ideality factor:    N/A")
        print(f"  Series resistance:  {params.series_resistance_ohm:.2f} Ω" if params.series_resistance_ohm else "  Series resistance:  N/A")


def example_detailed_analysis():
    """Example 2: Detailed analysis with custom callbacks and logging"""
    
    print("\n" + "=" * 60)
    print("Example 2: Detailed Analysis with Custom Processing")
    print("=" * 60)
    
    # Define custom callback for logging
    def log_progress(message):
        print(f"  [LOG] {message}")
    
    data_folder = Path("./results")
    
    if not data_folder.exists():
        print(f"Data folder not found: {data_folder}")
        return
    
    # Load data with logging
    print("\nLoading data...")
    results = load_folder_data(str(data_folder), log_callback=log_progress)
    
    # Process each measurement with detailed analysis
    print("\nDetailed parameter analysis:")
    for ivl in results.ivl_data:
        print(f"\n{'='*50}")
        print(f"Measurement Step {ivl.step}, Stress Level: {ivl.stress_level:.6f}")
        print(f"{'='*50}")
        
        # Basic info
        print(f"Data points: {len(ivl.voltage)}")
        print(f"Voltage range: {np.min(ivl.voltage):.4f} to {np.max(ivl.voltage):.4f} V")
        print(f"Current range: {np.min(ivl.current)*1e3:.4f} to {np.max(ivl.current)*1e3:.4f} mA")
        print(f"Power range:   {np.min(ivl.optical_power)*1e6:.4f} to {np.max(ivl.optical_power)*1e6:.4f} μW")
        
        # Threshold analysis
        print("\n--- Threshold Analysis ---")
        i_th, slope, i_arr, slope_arr = extract_threshold_max_slope(ivl.current, ivl.optical_power)
        
        if i_th is not None:
            print(f"Threshold current: {i_th*1e3:.6f} mA")
            print(f"Slope efficiency: {slope*1e3:.6f} mW/A")
            
            # Find voltage at threshold
            th_idx = np.argmin(np.abs(np.abs(ivl.current) - i_th))
            v_th = ivl.voltage[th_idx]
            print(f"Voltage at threshold: {v_th:.6f} V")
        else:
            print("Could not determine threshold current")
        
        # Power conversion efficiency
        print("\n--- Power Conversion Efficiency ---")
        i_pce, pce, max_pce, i_at_max_pce, v_at_max_pce = calculate_power_conversion_efficiency(
            ivl.voltage, ivl.current, ivl.optical_power
        )
        
        print(f"Maximum PCE: {max_pce:.4f}%")
        print(f"Optimal current: {i_at_max_pce*1e3:.6f} mA")
        print(f"Voltage at optimal current: {v_at_max_pce:.6f} V")
        
        # Statistics
        print("\n--- Statistics ---")
        print(f"Mean PCE: {np.mean(pce):.4f}%")
        print(f"Std PCE: {np.std(pce):.4f}%")
        
        # Extract all parameters
        params = extract_all_parameters(ivl)
        results.parameters.append(params)
        
        print(f"\n✓ Processed step {params.step}")


def example_single_file_analysis():
    """Example 3: Analyze a single measurement file"""
    
    print("\n" + "=" * 60)
    print("Example 3: Single File Analysis")
    print("=" * 60)
    
    # Try to find a measurement file
    data_folder = Path("./results")
    csv_files = list(data_folder.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_folder}")
        print("Please create a './results' folder with CSV measurement files")
        return
    
    # Use the first found CSV file
    data_file = csv_files[0]
    print(f"\nAnalyzing file: {data_file.name}")
    
    # Load the measurement
    ivl = load_measurement_csv(str(data_file))
    
    if ivl is None:
        print("Failed to load measurement file")
        return
    
    print(f"✓ Loaded {len(ivl.voltage)} data points")
    
    # Extract parameters
    params = extract_all_parameters(ivl)
    
    print("\nExtracted Parameters:")
    print(f"  Step: {params.step}")
    print(f"  Stress Level: {params.stress_level:.6f}")
    print(f"  Threshold Current: {params.threshold_current_A*1e3:.6f} mA" if params.threshold_current_A else "  Threshold Current: N/A")
    print(f"  Slope Efficiency: {params.slope_efficiency_W_A*1e3:.6f} mW/A" if params.slope_efficiency_W_A else "  Slope Efficiency: N/A")
    print(f"  Max Power: {params.max_power_W*1e6:.6f} μW" if params.max_power_W else "  Max Power: N/A")
    print(f"  Max PCE: {params.max_pce_pct:.4f}%" if params.max_pce_pct else "  Max PCE: N/A")
    print(f"  Ideality Factor: {params.ideality_factor:.6f}" if params.ideality_factor else "  Ideality Factor: N/A")
    print(f"  Series Resistance: {params.series_resistance_ohm:.2f} Ω" if params.series_resistance_ohm else "  Series Resistance: N/A")


def run_all_examples():
    """Run all examples"""
    
    print("\n" + "#" * 60)
    print("# Step Stress Analysis - Usage Examples")
    print("#" * 60)
    
    try:
        example_basic_analysis()
    except Exception as e:
        print(f"Error in example_basic_analysis: {e}")
    
    try:
        example_detailed_analysis()
    except Exception as e:
        print(f"Error in example_detailed_analysis: {e}")
    
    try:
        example_single_file_analysis()
    except Exception as e:
        print(f"Error in example_single_file_analysis: {e}")
    
    print("\n" + "#" * 60)
    print("# Examples completed!")
    print("#" * 60)


if __name__ == "__main__":
    run_all_examples()
