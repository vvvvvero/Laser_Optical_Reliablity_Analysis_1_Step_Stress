#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analysis worker thread for step stress analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal

from .models import AnalysisResults
from .data_loader import load_folder_data, load_iv_power_csv, load_measurement_csv, load_stress_csv
from .parameter_extractor import extract_all_parameters


class AnalysisWorker(QThread):
    """Worker thread for data analysis"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, data_path: str):
        super().__init__()
        self.data_path = data_path
    
    def run(self):
        try:
            data_path = Path(self.data_path)
            
            self.progress.emit("Loading data...")
            
            if data_path.is_dir():
                results = load_folder_data(str(data_path), self.progress.emit)
            else:
                results = AnalysisResults()
                if 'iv_power' in data_path.name.lower():
                    ivl = load_iv_power_csv(str(data_path))
                    if ivl:
                        results.ivl_data.append(ivl)
                        self.progress.emit(f"Loaded: {data_path.name}")
                elif 'stress' in data_path.name.lower():
                    stress = load_stress_csv(str(data_path))
                    if stress:
                        results.stress_data.append(stress)
                        self.progress.emit(f"Loaded stress: {data_path.name}")
                else:
                    ivl = load_measurement_csv(str(data_path))
                    if ivl:
                        results.ivl_data.append(ivl)
                        self.progress.emit(f"Loaded: {data_path.name}")
            
            # Extract parameters
            self.progress.emit("Extracting parameters...")
            for ivl in results.ivl_data:
                params = extract_all_parameters(ivl)
                results.parameters.append(params)
                self.progress.emit(f"  Step {params.step}: Extracted parameters")
            
            self.progress.emit("Analysis complete!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
