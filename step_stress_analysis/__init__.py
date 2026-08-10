#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Step Stress Data Analysis Library

A comprehensive Python package for analyzing step stress measurement data from 
semiconductor devices (VCSELs, laser diodes, etc.).

Author: Veronica GaoZhan
Date: February 2026
"""

__version__ = "1.0.0"
__author__ = "Veronica GaoZhan"
__email__ = "veronica.gao.zhan@example.com"

from .models import (
    IVLData,
    StressData,
    ExtractedParameters,
    AnalysisResults
)

from .data_loader import (
    load_measurement_csv,
    load_iv_power_csv,
    load_stress_csv,
    load_folder_data
)

from .parameter_extractor import (
    extract_all_parameters,
    extract_threshold_max_slope,
    extract_threshold_combined,
    calculate_power_conversion_efficiency,
    calculate_slope_efficiency_vs_current,
    extract_ideality_factor,
    extract_series_resistance
)

from .analysis_worker import AnalysisWorker
from .gui import StepStressAnalysisGUI

__all__ = [
    # Models
    'IVLData',
    'StressData',
    'ExtractedParameters',
    'AnalysisResults',
    
    # Data loading
    'load_measurement_csv',
    'load_iv_power_csv',
    'load_stress_csv',
    'load_folder_data',
    
    # Parameter extraction
    'extract_all_parameters',
    'extract_threshold_max_slope',
    'extract_threshold_combined',
    'calculate_power_conversion_efficiency',
    'calculate_slope_efficiency_vs_current',
    'extract_ideality_factor',
    'extract_series_resistance',
    
    # GUI and threading
    'AnalysisWorker',
    'StepStressAnalysisGUI'
]
