#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data models and structures for step stress analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IVLData:
    """Single IVL measurement data (at one stress level)"""
    step: int
    stress_level: float
    voltage: np.ndarray
    current: np.ndarray
    optical_power: np.ndarray
    setpoint: np.ndarray
    timestamp: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class StressData:
    """Stress monitoring data"""
    step: int
    stress_level: float
    time: np.ndarray
    voltage: np.ndarray
    current: np.ndarray
    optical_power: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class ExtractedParameters:
    """Parameters extracted from a single IVL measurement"""
    step: int
    stress_level: float
    
    # L-I parameters
    threshold_current_A: Optional[float] = None
    threshold_voltage_V: Optional[float] = None
    slope_efficiency_W_A: Optional[float] = None
    threshold_method: str = 'none'  # Method used for threshold extraction
    
    # Rollover parameters
    rollover_current_A: Optional[float] = None
    rollover_voltage_V: Optional[float] = None
    rollover_power_W: Optional[float] = None
    
    # Maximum power parameters
    max_power_W: Optional[float] = None
    current_at_max_power_A: Optional[float] = None
    voltage_at_max_power_V: Optional[float] = None
    
    # Power conversion efficiency (PCE) parameters
    max_pce_pct: Optional[float] = None  # Maximum PCE (%)
    current_at_max_pce_A: Optional[float] = None
    voltage_at_max_pce_V: Optional[float] = None
    
    # V-I parameters
    ideality_factor: Optional[float] = None
    series_resistance_ohm: Optional[float] = None
    I0_A: Optional[float] = None
    
    # Additional parameters
    differential_resistance_ohm: Optional[float] = None
    wall_plug_efficiency: Optional[float] = None
    knee_voltage_V: Optional[float] = None
    fit_quality_r2: Optional[float] = None


@dataclass
class AnalysisResults:
    """Complete analysis results"""
    ivl_data: List[IVLData] = field(default_factory=list)
    stress_data: List[StressData] = field(default_factory=list)
    parameters: List[ExtractedParameters] = field(default_factory=list)
