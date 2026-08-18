#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom parameter extraction example.

This example shows how to access individual parameter extraction
functions and use them for custom analysis workflows.

Author: Veronica GaoZhan
Date: February 2026
"""

import numpy as np
import matplotlib.pyplot as plt

from step_stress_analysis import (
    load_measurement_csv,
    extract_threshold_max_slope,
    extract_threshold_combined,
    extract_ideality_factor,
    calculate_power_conversion_efficiency,
    calculate_slope_efficiency_vs_current,
)


def analyze_single_measurement(csv_file: str):
    """Analyze a single measurement file with detailed extraction methods."""
    
    print(f"Loading: {csv_file}")
    ivl = load_measurement_csv(csv_file)
    
    if not ivl:
        print("Failed to load file")
        return
    
    print(f"Step: {ivl.step}, Stress Level: {ivl.stress_level}\n")
    
    # Method 1: Maximum slope method for threshold extraction
    print("=== Threshold Extraction Methods ===\n")
    
    i_th_slope, v_th_slope, curr_slope, slope_eff = extract_threshold_max_slope(
        ivl.current, ivl.optical_power
    )
    print(f"Maximum Slope Method:")
    print(f"  Threshold Current: {i_th_slope*1e3:.3f} mA")
    print(f"  Threshold Voltage: {v_th_slope:.3f} V")
    print(f"  Max Slope Efficiency: {slope_eff[np.argmax(slope_eff)]*1e3:.3f} mW/A\n")
    
    # Method 2: Combined method (more robust)
    i_th_comb, v_th_comb, method = extract_threshold_combined(ivl.current, ivl.optical_power)
    print(f"Combined Method (most robust):")
    print(f"  Threshold Current: {i_th_comb*1e3:.3f} mA")
    print(f"  Threshold Voltage: {v_th_comb:.3f} V")
    print(f"  Method Used: {method}\n")
    
    # Method 3: Slope efficiency calculation
    print("=== Efficiency Analysis ===\n")
    
    curr_eff, slope_eff_array = calculate_slope_efficiency_vs_current(ivl.current, ivl.optical_power)
    if len(slope_eff_array) > 0:
        max_slope_eff = np.max(slope_eff_array)
        print(f"Slope Efficiency (dP/dI): {max_slope_eff*1e3:.3f} mW/A")
    
    # Power conversion efficiency
    pce_percent = calculate_power_conversion_efficiency(
        ivl.voltage, ivl.current, ivl.optical_power
    )
    if isinstance(pce_percent, tuple):
        max_pce, curr_at_pce, volt_at_pce = pce_percent
        print(f"Max PCE: {max_pce:.2f}%")
        print(f"  at Current: {curr_at_pce*1e3:.3f} mA")
        print(f"  at Voltage: {volt_at_pce:.3f} V\n")
    
    # Method 4: Ideality factor from semi-log I-V
    print("=== Device Physics Parameters ===\n")
    
    n_ideal, i0, rs = extract_ideality_factor(ivl.voltage, ivl.current)
    print(f"Ideality Factor (from Shockley equation): {n_ideal:.2f}")
    print(f"  I0 (saturation current): {i0:.3e} A")
    print(f"  Series Resistance: {rs:.1f} Ω\n")
    
    # Create plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: L-I curve with threshold markers
    ax = axes[0, 0]
    ax.plot(ivl.current * 1e3, ivl.optical_power * 1e6, 'o-', linewidth=2, markersize=6)
    if i_th_comb:
        ax.axvline(i_th_comb * 1e3, color='red', linestyle='--', linewidth=2, label=f'Threshold: {i_th_comb*1e3:.2f} mA')
    ax.set_xlabel('Current (mA)')
    ax.set_ylabel('Optical Power (μW)')
    ax.set_title('L-I Curve with Threshold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Plot 2: Slope Efficiency
    ax = axes[0, 1]
    if len(curr_eff) > 0:
        ax.plot(curr_eff * 1e3, slope_eff_array * 1e3, '-', linewidth=2)
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Slope Efficiency (mW/A)')
        ax.set_title('dP/dI vs Current')
        ax.grid(True, alpha=0.3)
    
    # Plot 3: I-V characteristics (linear)
    ax = axes[1, 0]
    ax.plot(ivl.voltage, ivl.current * 1e3, 'o-', linewidth=2, markersize=6)
    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current (mA)')
    ax.set_title('I-V Characteristics')
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Semi-log I-V for ideality factor
    ax = axes[1, 1]
    i_positive = np.abs(ivl.current)
    i_positive[i_positive < 1e-15] = 1e-15
    ax.semilogy(ivl.voltage, i_positive, 'o-', linewidth=2, markersize=6)
    ax.set_xlabel('Voltage (V)')
    ax.set_ylabel('Current (A, log scale)')
    ax.set_title(f'Semi-log I-V (Ideality Factor: {n_ideal:.2f})')
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python custom_analysis.py <csv_file>")
        print("\nExample:")
        print("  python custom_analysis.py measurement_step_1.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    analyze_single_measurement(csv_file)
