#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch analysis example: Process multiple measurement folders.

This example demonstrates how to process multiple measurement 
datasets and export results to CSV files.

Author: Veronica GaoZhan
Date: February 2026
"""

import csv
from pathlib import Path
from typing import List

from step_stress_analysis import (
    load_folder_data,
    extract_all_parameters,
    ExtractedParameters,
)


def export_parameters_to_csv(parameters: List[ExtractedParameters], output_file: str):
    """Export extracted parameters to CSV file."""
    
    fieldnames = [
        'Step', 'Stress_Level',
        'Threshold_Current_A', 'Threshold_Voltage_V', 'Threshold_Method',
        'Slope_Efficiency_W_A', 'Max_Power_W', 'Current_at_Max_Power_A',
        'Voltage_at_Max_Power_V', 'Max_PCE_pct', 'Current_at_Max_PCE_A',
        'Voltage_at_Max_PCE_V', 'Ideality_Factor', 'Series_Resistance_Ohm'
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for p in parameters:
            writer.writerow({
                'Step': p.step,
                'Stress_Level': f"{p.stress_level:.6f}",
                'Threshold_Current_A': f"{p.threshold_current_A:.9e}" if p.threshold_current_A else '',
                'Threshold_Voltage_V': f"{p.threshold_voltage_V:.9e}" if p.threshold_voltage_V else '',
                'Threshold_Method': p.threshold_method,
                'Slope_Efficiency_W_A': f"{p.slope_efficiency_W_A:.9e}" if p.slope_efficiency_W_A else '',
                'Max_Power_W': f"{p.max_power_W:.9e}" if p.max_power_W else '',
                'Current_at_Max_Power_A': f"{p.current_at_max_power_A:.9e}" if p.current_at_max_power_A else '',
                'Voltage_at_Max_Power_V': f"{p.voltage_at_max_power_V:.9e}" if p.voltage_at_max_power_V else '',
                'Max_PCE_pct': f"{p.max_pce_pct:.4f}" if p.max_pce_pct else '',
                'Current_at_Max_PCE_A': f"{p.current_at_max_pce_A:.9e}" if p.current_at_max_pce_A else '',
                'Voltage_at_Max_PCE_V': f"{p.voltage_at_max_pce_V:.9e}" if p.voltage_at_max_pce_V else '',
                'Ideality_Factor': f"{p.ideality_factor:.4f}" if p.ideality_factor else '',
                'Series_Resistance_Ohm': f"{p.series_resistance_ohm:.4f}" if p.series_resistance_ohm else '',
            })
    
    print(f"Exported parameters to: {output_file}")


def main():
    """Process all measurement folders in current directory."""
    
    # Find all measurement folders
    data_dirs = list(Path(".").glob("measurement_*"))
    
    if not data_dirs:
        print("No measurement folders found (looking for measurement_* folders)")
        return
    
    print(f"Found {len(data_dirs)} measurement folders\n")
    
    for data_dir in sorted(data_dirs):
        print(f"Processing: {data_dir}")
        
        # Load data
        results = load_folder_data(str(data_dir))
        
        if not results.ivl_data:
            print(f"  No IVL data found, skipping...\n")
            continue
        
        # Extract parameters
        for ivl in results.ivl_data:
            param = extract_all_parameters(ivl)
            results.parameters.append(param)
        
        # Export results
        output_file = data_dir / f"{data_dir.name}_parameters.csv"
        export_parameters_to_csv(results.parameters, str(output_file))
        
        print(f"  Analyzed {len(results.parameters)} measurements")
        print()
    
    print("Batch processing complete!")


if __name__ == "__main__":
    main()
