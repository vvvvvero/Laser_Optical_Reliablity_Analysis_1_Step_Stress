#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data loading functions for step stress analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

import csv
import numpy as np
from pathlib import Path
from typing import Optional, Callable

from .models import IVLData, StressData, AnalysisResults


def load_measurement_csv(filepath: str) -> Optional[IVLData]:
    """Load measurement CSV file (step stress format)"""
    try:
        data = {'Step': [], 'Stress_Level': [], 'Point': [], 'Timestamp': [],
                'Setpoint': [], 'Voltage_V': [], 'Current_A': [], 
                'Optical_Power_W': [], 'Status': []}
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key in data.keys():
                    if key in row:
                        data[key].append(row[key])
        
        if len(data['Voltage_V']) == 0:
            return None
        
        step = int(data['Step'][0]) if data['Step'] else 0
        stress_level = float(data['Stress_Level'][0]) if data['Stress_Level'] else 0.0
        
        return IVLData(
            step=step,
            stress_level=stress_level,
            voltage=np.array([float(v) for v in data['Voltage_V']]),
            current=np.array([float(c) for c in data['Current_A']]),
            optical_power=np.array([float(p) for p in data['Optical_Power_W']]),
            setpoint=np.array([float(s) for s in data['Setpoint']])
        )
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def load_iv_power_csv(filepath: str) -> Optional[IVLData]:
    """Load IV+Power CSV file (single measurement format)"""
    try:
        data = {'Point': [], 'Timestamp': [], 'Relative_Time_s': [], 'Setpoint': [],
                'Voltage_V': [], 'Current_A': [], 'Optical_Power_W': [], 'Status': []}
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key in data.keys():
                    if key in row:
                        data[key].append(row[key])
        
        if len(data['Voltage_V']) == 0:
            return None
        
        return IVLData(
            step=0,
            stress_level=0.0,
            voltage=np.array([float(v) for v in data['Voltage_V']]),
            current=np.array([float(c) for c in data['Current_A']]),
            optical_power=np.array([float(p) for p in data['Optical_Power_W']]),
            setpoint=np.array([float(s) for s in data['Setpoint']])
        )
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def load_stress_csv(filepath: str, step: int = 0, stress_level: float = 0.0) -> Optional[StressData]:
    """Load stress monitoring CSV file"""
    try:
        time_data = []
        voltage_data = []
        current_data = []
        power_data = []
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        header_idx = 0
        for i, line in enumerate(lines):
            if not line.startswith('#') and line.strip():
                header_idx = i
                break
        
        reader = csv.DictReader(lines[header_idx:])
        for row in reader:
            try:
                if 'Relative_Time_s' in row:
                    time_data.append(float(row['Relative_Time_s']))
                elif 'Elapsed_s' in row:
                    time_data.append(float(row['Elapsed_s']))
                
                if 'Voltage_V' in row:
                    voltage_data.append(float(row['Voltage_V']))
                if 'Current_A' in row:
                    current_data.append(float(row['Current_A']))
                if 'Optical_Power_W' in row:
                    power_data.append(float(row['Optical_Power_W']))
            except (ValueError, KeyError):
                continue
        
        if len(voltage_data) == 0:
            return None
        
        return StressData(
            step=step,
            stress_level=stress_level,
            time=np.array(time_data),
            voltage=np.array(voltage_data),
            current=np.array(current_data),
            optical_power=np.array(power_data) if power_data else np.array([])
        )
    except Exception as e:
        print(f"Error loading stress file {filepath}: {e}")
        return None


def load_folder_data(folder_path: str, log_callback: Optional[Callable] = None) -> AnalysisResults:
    """Load all data from a step stress measurement folder"""
    results = AnalysisResults()
    folder = Path(folder_path)
    
    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)
    
    if not folder.exists():
        log(f"Folder not found: {folder_path}")
        return results
    
    # Find and load measurement files
    measurement_files = sorted(folder.glob("measurement_step_*.csv"))
    for meas_file in measurement_files:
        ivl = load_measurement_csv(str(meas_file))
        if ivl:
            results.ivl_data.append(ivl)
            log(f"  Loaded: {meas_file.name} (Step {ivl.step}, Stress {ivl.stress_level:.4f})")
    
    # Try IV+Power files if no step stress files found
    if not results.ivl_data:
        iv_power_files = sorted(folder.glob("*_iv_power_*.csv"))
        for iv_file in iv_power_files:
            ivl = load_iv_power_csv(str(iv_file))
            if ivl:
                results.ivl_data.append(ivl)
                log(f"  Loaded: {iv_file.name}")
    
    # Find and load stress monitoring files
    stress_files = sorted(folder.glob("stress_step_*.csv"))
    for stress_file in stress_files:
        try:
            step_num = int(stress_file.stem.split('_')[2])
        except:
            step_num = 0
        
        stress = load_stress_csv(str(stress_file), step=step_num)
        if stress:
            results.stress_data.append(stress)
            log(f"  Loaded: {stress_file.name}")
    
    # Also try single-file stress formats
    if not results.stress_data:
        stress_current_file = folder / "stress_current_monitor.csv"
        if stress_current_file.exists():
            stress = load_stress_csv(str(stress_current_file))
            if stress:
                results.stress_data.append(stress)
                log(f"  Loaded: stress_current_monitor.csv")
    
    log(f"Total: {len(results.ivl_data)} IVL measurements, {len(results.stress_data)} stress records")
    return results
