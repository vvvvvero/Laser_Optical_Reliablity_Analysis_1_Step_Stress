#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visualization functions for step stress data analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

import numpy as np
from typing import Optional, List, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from .models import IVLData, ExtractedParameters


def plot_ivl_characteristics(figure: Figure, ivl_data: List[IVLData], parameters: Optional[List[ExtractedParameters]] = None):
    """
    Plot I-V, L-I, L-V and semi-log I-V characteristics.
    
    Args:
        figure: Matplotlib Figure object
        ivl_data: List of IVLData objects
        parameters: Optional list of extracted parameters for annotations
    """
    figure.clear()
    
    ax_iv = figure.add_subplot(221)
    ax_li = figure.add_subplot(222)
    ax_lv = figure.add_subplot(223)
    ax_semilog = figure.add_subplot(224)
    
    # Color mapping based on stress level
    stress_levels = [ivl.stress_level for ivl in ivl_data]
    if len(set(stress_levels)) > 1:
        norm = Normalize(vmin=min(stress_levels), vmax=max(stress_levels))
    else:
        norm = Normalize(vmin=0, vmax=1)
    cmap = plt.cm.viridis
    
    for i, ivl in enumerate(ivl_data):
        color = cmap(norm(ivl.stress_level))
        label = f"Step {ivl.step} ({ivl.stress_level:.3f})"
        
        # I-V plot
        ax_iv.plot(ivl.voltage, ivl.current * 1e3, '-', 
                   color=color, linewidth=1.5, label=label)
        
        # L-I plot
        ax_li.plot(ivl.current * 1e3, ivl.optical_power * 1e6, '-',
                   color=color, linewidth=1.5, label=label)
        
        # L-V plot
        ax_lv.plot(ivl.voltage, ivl.optical_power * 1e6, '-',
                   color=color, linewidth=1.5, label=label)
        
        # Semi-log I-V plot
        i_positive = np.abs(ivl.current)
        i_positive[i_positive < 1e-15] = 1e-15
        ax_semilog.semilogy(ivl.voltage, i_positive, '-',
                            color=color, linewidth=1.5, label=label)
        
        # Add threshold annotations if available
        if parameters and i < len(parameters):
            param = parameters[i]
            if param.threshold_current_A is not None:
                ax_li.plot(param.threshold_current_A * 1e3, 0, 'x', 
                          color=color, markersize=8, markeredgewidth=2)
    
    ax_iv.set_xlabel('Voltage (V)')
    ax_iv.set_ylabel('Current (mA)')
    ax_iv.set_title('I-V Characteristics')
    ax_iv.grid(True, alpha=0.3)
    
    ax_li.set_xlabel('Current (mA)')
    ax_li.set_ylabel('Optical Power (μW)')
    ax_li.set_title('L-I Characteristics')
    ax_li.grid(True, alpha=0.3)
    
    ax_lv.set_xlabel('Voltage (V)')
    ax_lv.set_ylabel('Optical Power (μW)')
    ax_lv.set_title('L-V Characteristics')
    ax_lv.grid(True, alpha=0.3)
    
    ax_semilog.set_xlabel('Voltage (V)')
    ax_semilog.set_ylabel('Current (A)')
    ax_semilog.set_title('Semi-log I-V (for ideality factor)')
    ax_semilog.grid(True, alpha=0.3)
    
    # Add legend if few curves
    if len(ivl_data) <= 10:
        ax_iv.legend(fontsize=7, loc='best')
    
    figure.tight_layout()


def plot_stress_monitoring(figure: Figure, continuous_stress: Dict[str, np.ndarray]):
    """
    Plot continuous stress monitoring data.
    
    Args:
        figure: Matplotlib Figure object
        continuous_stress: Dictionary with keys: time_s, current_A, voltage_V, optical_power_W, step_start_times_s
    """
    figure.clear()
    
    ax_pv = figure.add_subplot(211)
    ax_i = figure.add_subplot(212, sharex=ax_pv)
    ax_v = ax_pv.twinx()
    
    if not continuous_stress or len(continuous_stress.get('time_s', [])) == 0:
        ax_pv.set_title('No Stress Data')
        figure.tight_layout()
        return
    
    time_s = continuous_stress['time_s']
    current_mA = continuous_stress['current_A'] * 1e3
    voltage_V = continuous_stress['voltage_V']
    power_uW = continuous_stress['optical_power_W'] * 1e6
    
    power_valid = np.isfinite(power_uW)
    if np.any(power_valid):
        ax_pv.plot(time_s[power_valid], power_uW[power_valid], '-', color='tab:orange',
                   linewidth=1.2, label='Optical Power (μW)')
    else:
        ax_pv.text(0.5, 0.9, 'No optical power in stress files',
                   transform=ax_pv.transAxes, ha='center', va='center',
                   fontsize=9, color='tab:orange')
    
    ax_v.plot(time_s, voltage_V, '-', color='tab:blue', linewidth=1.1, label='Voltage (V)')
    ax_i.plot(time_s, current_mA, '-', color='tab:green', linewidth=1.1, label='Current (mA)')
    
    # Add step boundary lines
    for boundary_time in continuous_stress.get('step_start_times_s', [])[1:]:
        ax_pv.axvline(boundary_time, color='0.5', linestyle='--', linewidth=0.8, alpha=0.6)
        ax_i.axvline(boundary_time, color='0.5', linestyle='--', linewidth=0.8, alpha=0.6)
    
    ax_pv.set_ylabel('Optical Power (μW)', color='tab:orange')
    ax_v.set_ylabel('Voltage (V)', color='tab:blue')
    ax_pv.set_title('Continuous Stress: Optical Power (y1) and Voltage (y2) vs Time')
    ax_pv.grid(True, alpha=0.3)
    
    handles_p, labels_p = ax_pv.get_legend_handles_labels()
    handles_v, labels_v = ax_v.get_legend_handles_labels()
    if handles_p or handles_v:
        ax_pv.legend(handles_p + handles_v, labels_p + labels_v, loc='best', fontsize=8)
    
    ax_i.set_xlabel('Continuous Time (s)')
    ax_i.set_ylabel('Current (mA)')
    ax_i.set_title('Continuous Stress: Current vs Time')
    ax_i.grid(True, alpha=0.3)
    ax_i.legend(loc='best', fontsize=8)
    
    figure.tight_layout()


def plot_parameter_trends(figure: Figure, parameters: List[ExtractedParameters]):
    """
    Plot trends of extracted parameters over stress cycles.
    
    Args:
        figure: Matplotlib Figure object
        parameters: List of ExtractedParameters objects
    """
    figure.clear()
    
    if not parameters:
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No parameters to plot', ha='center', va='center')
        return
    
    steps = [p.step for p in parameters]
    
    # Subplot layout for 6 subplots
    axes = [figure.add_subplot(2, 3, i) for i in range(1, 7)]
    
    # Plot 1: Threshold Current
    th_currents = [p.threshold_current_A * 1e3 if p.threshold_current_A else None for p in parameters]
    if any(th_currents):
        axes[0].plot(steps, [x for x in th_currents if x is not None], 'o-', label='Threshold I')
        axes[0].set_ylabel('Threshold Current (mA)')
        axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Threshold Voltage
    th_voltages = [p.threshold_voltage_V if p.threshold_voltage_V else None for p in parameters]
    if any(th_voltages):
        axes[1].plot(steps, [x for x in th_voltages if x is not None], 's-', color='tab:orange', label='Threshold V')
        axes[1].set_ylabel('Threshold Voltage (V)')
        axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Slope Efficiency
    slopes = [p.slope_efficiency_W_A * 1e3 if p.slope_efficiency_W_A else None for p in parameters]
    if any(slopes):
        axes[2].plot(steps, [x for x in slopes if x is not None], '^-', color='tab:green', label='Slope Efficiency')
        axes[2].set_ylabel('Slope Efficiency (mW/A)')
        axes[2].grid(True, alpha=0.3)
    
    # Plot 4: Max Power
    max_powers = [p.max_power_W * 1e6 if p.max_power_W else None for p in parameters]
    if any(max_powers):
        axes[3].plot(steps, [x for x in max_powers if x is not None], 'D-', color='tab:red', label='Max Power')
        axes[3].set_ylabel('Max Power (μW)')
        axes[3].grid(True, alpha=0.3)
    
    # Plot 5: Max PCE
    max_pces = [p.max_pce_pct if p.max_pce_pct else None for p in parameters]
    if any(max_pces):
        axes[4].plot(steps, [x for x in max_pces if x is not None], 'v-', color='tab:purple', label='Max PCE')
        axes[4].set_ylabel('Max PCE (%)')
        axes[4].grid(True, alpha=0.3)
    
    # Plot 6: Ideality Factor
    idealities = [p.ideality_factor if p.ideality_factor else None for p in parameters]
    if any(idealities):
        axes[5].plot(steps, [x for x in idealities if x is not None], 'p-', color='tab:brown', label='Ideality Factor')
        axes[5].set_ylabel('Ideality Factor')
        axes[5].grid(True, alpha=0.3)
    
    for ax in axes:
        ax.set_xlabel('Step')
        if ax.has_data():
            ax.legend(loc='best', fontsize=8)
    
    figure.tight_layout()


def plot_pce_analysis(figure: Figure, parameters: List[ExtractedParameters]):
    """
    Plot power conversion efficiency analysis.
    
    Args:
        figure: Matplotlib Figure object
        parameters: List of ExtractedParameters objects
    """
    figure.clear()
    
    if not parameters:
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No parameters to plot', ha='center', va='center')
        return
    
    steps = [p.step for p in parameters]
    
    # Create subplots
    ax1 = figure.add_subplot(221)
    ax2 = figure.add_subplot(222)
    ax3 = figure.add_subplot(223)
    ax4 = figure.add_subplot(224)
    
    # PCE vs step
    pces = [p.max_pce_pct if p.max_pce_pct else None for p in parameters]
    if any(pces):
        valid_steps = [s for s, p in zip(steps, pces) if p is not None]
        valid_pces = [p for p in pces if p is not None]
        ax1.plot(valid_steps, valid_pces, 'o-', label='Max PCE', linewidth=2, markersize=6)
        ax1.set_xlabel('Step')
        ax1.set_ylabel('Max PCE (%)')
        ax1.set_title('Maximum PCE vs Stress Step')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
    
    # PCE current at max efficiency
    pce_currents = [p.current_at_max_pce_A * 1e3 if p.current_at_max_pce_A else None for p in parameters]
    if any(pce_currents):
        valid_steps = [s for s, p in zip(steps, pce_currents) if p is not None]
        valid_currents = [p for p in pce_currents if p is not None]
        ax2.plot(valid_steps, valid_currents, 's-', color='tab:orange', label='Current @ Max PCE', linewidth=2, markersize=6)
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Current (mA)')
        ax2.set_title('Current at Max PCE vs Step')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    
    # PCE voltage at max efficiency
    pce_voltages = [p.voltage_at_max_pce_V if p.voltage_at_max_pce_V else None for p in parameters]
    if any(pce_voltages):
        valid_steps = [s for s, p in zip(steps, pce_voltages) if p is not None]
        valid_voltages = [p for p in pce_voltages if p is not None]
        ax3.plot(valid_steps, valid_voltages, '^-', color='tab:green', label='Voltage @ Max PCE', linewidth=2, markersize=6)
        ax3.set_xlabel('Step')
        ax3.set_ylabel('Voltage (V)')
        ax3.set_title('Voltage at Max PCE vs Step')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
    
    # Max power at PCE point
    pce_powers = [p.max_power_W * 1e6 if p.max_power_W else None for p in parameters]
    if any(pce_powers):
        valid_steps = [s for s, p in zip(steps, pce_powers) if p is not None]
        valid_powers = [p for p in pce_powers if p is not None]
        ax4.plot(valid_steps, valid_powers, 'D-', color='tab:red', label='Max Power', linewidth=2, markersize=6)
        ax4.set_xlabel('Step')
        ax4.set_ylabel('Max Power (μW)')
        ax4.set_title('Maximum Power vs Step')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
    
    figure.tight_layout()


def plot_relative_stress(figure: Figure, relative_data: List[Dict[str, Any]]):
    """
    Plot relative stress data per step.
    
    Args:
        figure: Matplotlib Figure object
        relative_data: List of dictionaries with relative stress info
    """
    figure.clear()
    
    ax_v = figure.add_subplot(211)
    ax_p = figure.add_subplot(212)
    
    if not relative_data:
        ax_v.text(0.5, 0.5, 'No relative stress data', ha='center', va='center')
        return
    
    # Group by step
    steps_dict = {}
    for row in relative_data:
        step = row['Step']
        if step not in steps_dict:
            steps_dict[step] = []
        steps_dict[step].append(row)
    
    # Plot relative voltage for each step
    for step in sorted(steps_dict.keys()):
        rows = steps_dict[step]
        times = [r['Relative_Time_s'] for r in rows]
        rel_voltages = [r.get('Relative_Voltage', 0) for r in rows]
        ax_v.plot(times, rel_voltages, 'o-', label=f'Step {step}', alpha=0.7)
    
    ax_v.set_ylabel('Relative Voltage (normalized)')
    ax_v.set_title('Relative Voltage per Step')
    ax_v.grid(True, alpha=0.3)
    ax_v.legend(loc='best', fontsize=8)
    
    # Plot relative power for each step
    for step in sorted(steps_dict.keys()):
        rows = steps_dict[step]
        times = [r['Relative_Time_s'] for r in rows]
        rel_powers = [r.get('Relative_Optical_Power', 0) for r in rows]
        ax_p.plot(times, rel_powers, 's-', label=f'Step {step}', alpha=0.7)
    
    ax_p.set_xlabel('Relative Time within Step (s)')
    ax_p.set_ylabel('Relative Power (normalized)')
    ax_p.set_title('Relative Optical Power per Step')
    ax_p.grid(True, alpha=0.3)
    ax_p.legend(loc='best', fontsize=8)
    
    figure.tight_layout()


def plot_fitting_examples(figure: Figure, parameters: List[ExtractedParameters], ivl_data: List[IVLData]):
    """
    Plot fitting examples showing threshold extraction methods.
    
    Args:
        figure: Matplotlib Figure object
        parameters: List of ExtractedParameters objects
        ivl_data: List of IVLData objects
    """
    figure.clear()
    
    if not ivl_data or not parameters:
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No data for fitting plots', ha='center', va='center')
        return
    
    # Show fitting for first few measurements
    num_plots = min(4, len(ivl_data))
    
    for i in range(num_plots):
        ax = figure.add_subplot(2, 2, i + 1)
        
        ivl = ivl_data[i]
        param = parameters[i] if i < len(parameters) else None
        
        # Plot L-I curve
        ax.plot(ivl.current * 1e3, ivl.optical_power * 1e6, 'o-', 
               label='Measurement', linewidth=2, markersize=4)
        
        # Mark threshold if available
        if param and param.threshold_current_A is not None:
            ax.axvline(param.threshold_current_A * 1e3, color='red', 
                      linestyle='--', linewidth=2, label=f'Threshold: {param.threshold_current_A*1e3:.2f} mA')
        
        # Mark max power if available
        if param and param.current_at_max_power_A is not None:
            ax.plot(param.current_at_max_power_A * 1e3, param.max_power_W * 1e6, 
                   'r*', markersize=15, label=f'Max Power')
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Optical Power (μW)')
        ax.set_title(f'Step {ivl.step} - {ivl.stress_level:.3f}')
        ax.grid(True, alpha=0.3)
        if param:
            ax.legend(fontsize=7, loc='best')
    
    figure.tight_layout()
