#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parameter extraction functions for step stress analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

import numpy as np
from typing import Tuple, Optional, Dict

from .models import IVLData, ExtractedParameters


def calculate_slope_efficiency_vs_current(current: np.ndarray, power: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate slope efficiency (dP/dI) as a function of current.
    
    Returns: (current_array, slope_efficiency_array) in SI units (W/A)
    """
    power_abs = np.abs(power)
    current_abs = np.abs(current)
    
    # Sort by current
    sort_idx = np.argsort(current_abs)
    i_sorted = current_abs[sort_idx]
    p_sorted = power_abs[sort_idx]
    
    if len(i_sorted) < 3:
        return np.array([]), np.array([])
    
    # Smooth data to reduce noise
    from scipy.ndimage import gaussian_filter1d
    p_smooth = gaussian_filter1d(p_sorted, sigma=2)
    
    # Calculate dP/dI (slope efficiency)
    dP_dI = np.gradient(p_smooth, i_sorted)
    
    # Clip negative values to 0 (slope should be positive)
    dP_dI = np.clip(dP_dI, 0, None)
    
    return i_sorted, dP_dI


def extract_threshold_max_slope(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float], np.ndarray, np.ndarray]:
    """Extract threshold current using maximum slope method.
    
    The threshold current is where dP/dI (slope efficiency) is maximum.
    This is the standard method: fit a line through the steepest part of L-I curve,
    and the x-intercept is the threshold current.
    
    Returns: (threshold_current, max_slope_efficiency, current_array, slope_array)
    """
    if len(current) < 10:
        return None, None, np.array([]), np.array([])
    
    power_abs = np.abs(power)
    current_abs = np.abs(current)
    
    # Sort by current
    sort_idx = np.argsort(current_abs)
    i_sorted = current_abs[sort_idx]
    p_sorted = power_abs[sort_idx]
    
    # Smooth data to reduce noise
    from scipy.ndimage import gaussian_filter1d
    p_smooth = gaussian_filter1d(p_sorted, sigma=2)
    
    # Calculate dP/dI (slope efficiency)
    dP_dI = np.gradient(p_smooth, i_sorted)
    
    # Find the maximum slope region (skip first few noisy points)
    margin = max(3, len(dP_dI) // 20)  # Skip first 5% of points
    
    # Find rollover point (where power starts decreasing or slope becomes negative)
    max_power_idx = np.argmax(p_sorted)
    
    # Search for max slope only up to rollover
    search_end = min(max_power_idx + 1, len(dP_dI) - margin)
    if search_end <= margin:
        search_end = len(dP_dI) - margin
    
    search_region = dP_dI[margin:search_end]
    
    if len(search_region) == 0:
        return None, None, i_sorted, np.clip(dP_dI, 0, None)
    
    max_slope_idx = np.argmax(search_region) + margin
    max_slope = dP_dI[max_slope_idx]
    
    if max_slope <= 0:
        return None, None, i_sorted, np.clip(dP_dI, 0, None)
    
    # Use a window around max slope point to fit a line
    window = max(5, len(i_sorted) // 10)
    fit_start = max(0, max_slope_idx - window)
    fit_end = min(len(i_sorted), max_slope_idx + window)
    
    i_fit = i_sorted[fit_start:fit_end]
    p_fit = p_sorted[fit_start:fit_end]
    
    if len(i_fit) < 3:
        # Just use the point of max slope
        i_th = i_sorted[max_slope_idx]
        return i_th, max_slope, i_sorted, np.clip(dP_dI, 0, None)
    
    try:
        # Linear fit: P = slope * (I - I_th)
        coeffs = np.polyfit(i_fit, p_fit, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        if slope > 0:
            # x-intercept: I_th = -intercept / slope
            i_th = -intercept / slope
            
            # Validate: threshold should be positive and less than current at max slope
            if i_th > 0 and i_th < i_sorted[max_slope_idx]:
                return i_th, slope, i_sorted, np.clip(dP_dI, 0, None)
            else:
                # If extrapolation gives unreasonable result, use max slope point
                i_th = i_sorted[max_slope_idx]
                return i_th, max_slope, i_sorted, np.clip(dP_dI, 0, None)
        else:
            return None, None, i_sorted, np.clip(dP_dI, 0, None)
    except Exception:
        return None, None, i_sorted, np.clip(dP_dI, 0, None)


def extract_threshold_current_linear_fit(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Extract threshold current using maximum slope method (wrapper for compatibility)."""
    i_th, slope, _, _ = extract_threshold_max_slope(current, power)
    return i_th, slope


def extract_threshold_second_derivative(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Extract threshold current using second derivative method (Method 2).
    
    The threshold is found at the inflection point where d²P/dI² is maximum.
    """
    if len(current) < 10:
        return None, None
    
    try:
        power_abs = np.abs(power)
        current_abs = np.abs(current)
        
        # Sort by current
        sort_idx = np.argsort(current_abs)
        i_sorted = current_abs[sort_idx]
        p_sorted = power_abs[sort_idx]
        
        # Smooth the data
        from scipy.ndimage import gaussian_filter1d
        p_smooth = gaussian_filter1d(p_sorted, sigma=2)
        
        # Calculate first and second derivatives
        dP = np.gradient(p_smooth, i_sorted)
        d2P = np.gradient(dP, i_sorted)
        
        # Find maximum of second derivative (inflection point)
        # Skip first and last few points
        margin = max(3, len(d2P) // 10)
        search_region = d2P[margin:-margin]
        max_d2P_idx = np.argmax(search_region) + margin
        
        i_th = i_sorted[max_d2P_idx]
        
        # Calculate slope efficiency from points above threshold
        above_th_mask = i_sorted > i_th
        if np.sum(above_th_mask) >= 3:
            coeffs = np.polyfit(i_sorted[above_th_mask], p_sorted[above_th_mask], 1)
            slope = coeffs[0]
            # Only return positive slope
            if slope > 0:
                return i_th, slope
        
        return i_th, None
    except Exception:
        return None, None


def extract_threshold_log_derivative(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Extract threshold using log-log derivative method (Method 3).
    
    In log-log space, the slope changes from >1 (subthreshold) to ~1 (above threshold).
    """
    if len(current) < 10:
        return None, None
    
    try:
        power_abs = np.abs(power)
        current_abs = np.abs(current)
        
        # Filter out zero/negative values
        valid_mask = (power_abs > 0) & (current_abs > 0)
        if np.sum(valid_mask) < 10:
            return None, None
        
        i_valid = current_abs[valid_mask]
        p_valid = power_abs[valid_mask]
        
        # Sort by current
        sort_idx = np.argsort(i_valid)
        i_sorted = i_valid[sort_idx]
        p_sorted = p_valid[sort_idx]
        
        # Log transform
        log_i = np.log(i_sorted)
        log_p = np.log(p_sorted)
        
        # Calculate local slope in log-log space using sliding window
        window = max(3, len(log_i) // 10)
        slopes = []
        for j in range(window, len(log_i) - window):
            local_slope, _ = np.polyfit(log_i[j-window:j+window], log_p[j-window:j+window], 1)
            slopes.append(local_slope)
        
        slopes = np.array(slopes)
        
        # Find where slope drops to ~1 (linear region)
        # Threshold is where slope transitions from high (subthreshold) to ~1
        for j in range(len(slopes) - 1):
            if slopes[j] > 1.5 and slopes[j+1] < 1.5:
                i_th = i_sorted[j + window]
                
                # Calculate slope efficiency
                above_th_mask = i_sorted > i_th
                if np.sum(above_th_mask) >= 3:
                    coeffs = np.polyfit(i_sorted[above_th_mask], p_sorted[above_th_mask], 1)
                    slope = coeffs[0]
                    # Only return positive slope
                    if slope > 0:
                        return i_th, slope
                return i_th, None
        
        return None, None
    except Exception:
        return None, None


def extract_threshold_ratio_method(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Extract threshold using P/I ratio method (Method 4).
    
    Below threshold: P/I is small and relatively constant (spontaneous emission)
    Above threshold: P/I increases rapidly (stimulated emission)
    """
    if len(current) < 10:
        return None, None
    
    try:
        power_abs = np.abs(power)
        current_abs = np.abs(current)
        
        # Avoid division by zero
        valid_mask = current_abs > 1e-12
        if np.sum(valid_mask) < 10:
            return None, None
        
        i_valid = current_abs[valid_mask]
        p_valid = power_abs[valid_mask]
        
        # Sort by current
        sort_idx = np.argsort(i_valid)
        i_sorted = i_valid[sort_idx]
        p_sorted = p_valid[sort_idx]
        
        # Calculate P/I ratio (differential efficiency)
        ratio = p_sorted / i_sorted
        
        # Smooth the ratio
        from scipy.ndimage import gaussian_filter1d
        ratio_smooth = gaussian_filter1d(ratio, sigma=2)
        
        # Find where ratio starts increasing significantly
        # Calculate derivative of ratio
        d_ratio = np.gradient(ratio_smooth, i_sorted)
        
        # Find maximum derivative (steepest increase in efficiency)
        margin = max(2, len(d_ratio) // 10)
        max_idx = np.argmax(d_ratio[margin:-margin]) + margin
        
        i_th = i_sorted[max_idx]
        
        # Calculate slope efficiency
        above_th_mask = i_sorted > i_th
        if np.sum(above_th_mask) >= 3:
            coeffs = np.polyfit(i_sorted[above_th_mask], p_sorted[above_th_mask], 1)
            slope = coeffs[0]
            # Only return positive slope
            if slope > 0:
                return i_th, slope
        
        return i_th, None
    except Exception:
        return None, None


def extract_threshold_noise_floor(current: np.ndarray, power: np.ndarray, 
                                   noise_multiplier: float = 5.0) -> Tuple[Optional[float], Optional[float]]:
    """Extract threshold using noise floor method (Method 5).
    
    Threshold is where power first exceeds noise_multiplier × noise_floor.
    """
    if len(current) < 5:
        return None, None
    
    try:
        power_abs = np.abs(power)
        current_abs = np.abs(current)
        
        # Estimate noise floor from lowest 10% of power readings
        noise_floor = np.percentile(power_abs, 10)
        threshold_power = noise_multiplier * noise_floor
        
        # Sort by current
        sort_idx = np.argsort(current_abs)
        i_sorted = current_abs[sort_idx]
        p_sorted = power_abs[sort_idx]
        
        # Find first point above threshold
        above_threshold = p_sorted > threshold_power
        if not np.any(above_threshold):
            return None, None
        
        th_idx = np.argmax(above_threshold)
        i_th = i_sorted[th_idx]
        
        # Calculate slope efficiency from linear region
        max_power = np.max(power_abs)
        linear_mask = (p_sorted > 0.2 * max_power) & (p_sorted < 0.8 * max_power)
        if np.sum(linear_mask) >= 3:
            coeffs = np.polyfit(i_sorted[linear_mask], p_sorted[linear_mask], 1)
            slope = coeffs[0]
            # Only return positive slope
            if slope > 0:
                return i_th, slope
        
        return i_th, None
    except Exception:
        return None, None


def extract_threshold_combined(current: np.ndarray, power: np.ndarray) -> Tuple[Optional[float], Optional[float], str]:
    """Try multiple threshold extraction methods and return best result.
    
    Returns: (threshold_current, slope_efficiency, method_used)
    """
    results = []
    
    # Method 1: Linear fit
    i_th, slope = extract_threshold_current_linear_fit(current, power)
    if i_th is not None:
        results.append((i_th, slope, 'linear_fit'))
    
    # Method 2: Second derivative
    i_th, slope = extract_threshold_second_derivative(current, power)
    if i_th is not None:
        results.append((i_th, slope, 'second_derivative'))
    
    # Method 3: Log derivative
    i_th, slope = extract_threshold_log_derivative(current, power)
    if i_th is not None:
        results.append((i_th, slope, 'log_derivative'))
    
    # Method 4: Ratio method
    i_th, slope = extract_threshold_ratio_method(current, power)
    if i_th is not None:
        results.append((i_th, slope, 'ratio_method'))
    
    # Method 5: Noise floor
    i_th, slope = extract_threshold_noise_floor(current, power)
    if i_th is not None:
        results.append((i_th, slope, 'noise_floor'))
    
    if not results:
        return None, None, 'none'
    
    # Filter out results with negative or zero slopes
    valid_results = [(i_th, sl, m) for i_th, sl, m in results if sl is None or sl > 0]
    
    if not valid_results:
        # If all slopes are negative, return threshold only from first result
        return results[0][0], None, results[0][2]
    
    # Return the median threshold if multiple methods work
    if len(valid_results) >= 3:
        thresholds = [r[0] for r in valid_results if r[0] is not None]
        slopes = [r[1] for r in valid_results if r[1] is not None and r[1] > 0]
        median_th = np.median(thresholds)
        median_slope = np.median(slopes) if slopes else None
        return median_th, median_slope, 'combined_median'
    
    # Otherwise return the first successful result
    return valid_results[0]


def calculate_power_conversion_efficiency(voltage: np.ndarray, current: np.ndarray, 
                                           power: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, float, float]:
    """Calculate power conversion efficiency (PCE) as a function of current.
    
    PCE = P_optical / P_electrical = P_optical / (V × I)
    
    Returns: (current_array, pce_array, max_pce, current_at_max_pce, voltage_at_max_pce)
    PCE is returned as percentage (0-100%)
    """
    power_abs = np.abs(power)
    current_abs = np.abs(current)
    voltage_abs = np.abs(voltage)
    
    # Calculate electrical power
    p_electrical = voltage_abs * current_abs
    
    # Avoid division by zero - need meaningful electrical power
    valid_mask = p_electrical > 1e-12
    
    if not np.any(valid_mask):
        return np.array([]), np.array([]), 0.0, 0.0, 0.0
    
    # Calculate PCE (as percentage)
    pce = np.zeros_like(power_abs)
    pce[valid_mask] = 100 * power_abs[valid_mask] / p_electrical[valid_mask]
    
    # PCE must be between 0 and 100% (physically reasonable)
    # Values > 100% indicate measurement errors or noise
    pce = np.clip(pce, 0, 100)
    
    # For finding max PCE, only consider points where PCE is reasonable (< 100%)
    # and current is above noise floor (avoid noise at low currents)
    current_threshold = np.max(current_abs) * 0.05  # 5% of max current
    reasonable_mask = (pce > 0) & (pce <= 100) & (current_abs > current_threshold)
    
    if not np.any(reasonable_mask):
        # Fallback: use all valid points
        reasonable_mask = valid_mask
    
    # Find maximum PCE among reasonable points
    pce_reasonable = pce.copy()
    pce_reasonable[~reasonable_mask] = 0
    max_pce_idx = np.argmax(pce_reasonable)
    max_pce = pce[max_pce_idx]
    i_at_max_pce = current_abs[max_pce_idx]
    v_at_max_pce = voltage_abs[max_pce_idx]
    
    return current_abs, pce, max_pce, i_at_max_pce, v_at_max_pce


def extract_rollover_parameters(voltage: np.ndarray, current: np.ndarray, 
                                power: np.ndarray) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extract rollover parameters from L-I data."""
    if len(current) < 3:
        return None, None, None
    
    power_abs = np.abs(power)
    max_power_idx = np.argmax(power_abs)
    
    if max_power_idx < len(power_abs) - 3:
        post_max_power = power_abs[max_power_idx + 1:]
        if np.any(post_max_power < 0.95 * power_abs[max_power_idx]):
            return (current[max_power_idx], 
                   voltage[max_power_idx], 
                   power_abs[max_power_idx])
    
    return current[max_power_idx], voltage[max_power_idx], power_abs[max_power_idx]


def extract_max_power_parameters(voltage: np.ndarray, current: np.ndarray,
                                  power: np.ndarray) -> Tuple[float, float, float]:
    """Extract maximum power and corresponding I/V values"""
    power_abs = np.abs(power)
    max_idx = np.argmax(power_abs)
    return power_abs[max_idx], current[max_idx], voltage[max_idx]


def extract_ideality_factor(voltage: np.ndarray, current: np.ndarray) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Extract ideality factor from V-I characteristics.
    
    The exponential region is selected as:
    - Lower bound: ~10x noise floor (to avoid noise)
    - Upper bound: ~20% above lower bound (to stay in exponential region before series resistance dominates)
    """
    if len(voltage) < 10:
        return None, None, None
    
    current_abs = np.abs(current)
    valid_mask = current_abs > 0
    v_valid = voltage[valid_mask]
    i_valid = current_abs[valid_mask]
    
    if len(v_valid) < 5:
        return None, None, None
    
    # Estimate noise floor from lowest readings
    noise_floor = max(1e-12, np.percentile(i_valid, 5))
    
    # Define the exponential region:
    # Lower bound: 10x noise floor
    # Upper bound: ~20% above lower bound (i.e., 1.2x lower bound) or ~15x noise floor
    # This keeps us in the exponential region before series resistance dominates
    lower_current = noise_floor * 10
    upper_current = lower_current * 1.2  # 20% above lower bound
    
    exp_mask = (i_valid > lower_current) & (i_valid < upper_current)
    exp_indices = np.where(exp_mask)[0]
    
    # If not enough points, try slightly wider range
    if len(exp_indices) < 5:
        lower_current = noise_floor * 5
        upper_current = lower_current * 2.0  # 100% above lower bound
        exp_mask = (i_valid > lower_current) & (i_valid < upper_current)
        exp_indices = np.where(exp_mask)[0]
    
    # Last resort: use a percentage of max current but still small
    if len(exp_indices) < 4:
        max_current = np.max(i_valid)
        exp_mask = (i_valid > noise_floor * 5) & (i_valid < 0.1 * max_current)
        exp_indices = np.where(exp_mask)[0]
    
    if len(exp_indices) < 4:
        return None, None, None
    
    try:
        v_exp = v_valid[exp_indices]
        i_exp = i_valid[exp_indices]
        
        ln_i = np.log(i_exp)
        coeffs = np.polyfit(v_exp, ln_i, 1)
        B = coeffs[0]
        A = coeffs[1]
        
        Vt = 0.026
        n = 1 / (B * Vt) if B > 0 else None
        I0 = np.exp(A)
        
        ln_i_fit = np.polyval(coeffs, v_exp)
        ss_res = np.sum((ln_i - ln_i_fit) ** 2)
        ss_tot = np.sum((ln_i - np.mean(ln_i)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if n is not None and 0.5 < n < 10:
            return n, I0, r2
    except Exception:
        pass
    
    return None, None, None


def extract_series_resistance(voltage: np.ndarray, current: np.ndarray) -> Tuple[Optional[float], Optional[float]]:
    """Extract series resistance from V-I characteristics."""
    if len(voltage) < 5:
        return None, None
    
    current_abs = np.abs(current)
    max_current = np.max(current_abs)
    
    linear_mask = (current_abs > 0.4 * max_current) & (current_abs < 0.9 * max_current)
    linear_indices = np.where(linear_mask)[0]
    
    if len(linear_indices) < 3:
        linear_mask = current_abs > 0.3 * max_current
        linear_indices = np.where(linear_mask)[0]
    
    if len(linear_indices) < 3:
        return None, None
    
    try:
        v_lin = voltage[linear_indices]
        i_lin = current[linear_indices]
        
        coeffs = np.polyfit(i_lin, v_lin, 1)
        Rs = coeffs[0]
        
        if len(v_lin) > 1:
            dV = np.diff(v_lin)
            dI = np.diff(i_lin)
            valid_dI = np.abs(dI) > 1e-15
            if np.any(valid_dI):
                Rd = np.median(dV[valid_dI] / dI[valid_dI])
            else:
                Rd = Rs
        else:
            Rd = Rs
        
        return Rs, Rd
    except Exception:
        pass
    
    return None, None


def extract_additional_parameters(voltage: np.ndarray, current: np.ndarray,
                                   power: np.ndarray) -> Dict[str, Optional[float]]:
    """Extract additional useful parameters."""
    params = {}
    
    power_abs = np.abs(power)
    current_abs = np.abs(current)
    
    max_power_idx = np.argmax(power_abs)
    if voltage[max_power_idx] > 0 and current_abs[max_power_idx] > 0:
        P_elec = voltage[max_power_idx] * current_abs[max_power_idx]
        params['wall_plug_efficiency_pct'] = 100 * power_abs[max_power_idx] / P_elec
    else:
        params['wall_plug_efficiency_pct'] = None
    
    noise_current = np.percentile(current_abs, 10)
    knee_mask = current_abs > 10 * noise_current
    knee_indices = np.where(knee_mask)[0]
    if len(knee_indices) > 0:
        params['knee_voltage_V'] = voltage[knee_indices[0]]
    else:
        params['knee_voltage_V'] = None
    
    return params


def extract_all_parameters(ivl: IVLData) -> ExtractedParameters:
    """Extract all parameters from a single IVL measurement"""
    params = ExtractedParameters(step=ivl.step, stress_level=ivl.stress_level)
    
    v = ivl.voltage
    i = ivl.current
    p = ivl.optical_power
    
    # L-I parameters - use maximum slope method (finds where dP/dI is largest)
    i_th, slope_eff, _, _ = extract_threshold_max_slope(i, p)
    params.threshold_current_A = i_th
    params.slope_efficiency_W_A = slope_eff
    params.threshold_method = 'max_slope'
    
    # Find voltage at threshold current
    if i_th is not None:
        th_idx = np.argmin(np.abs(np.abs(i) - i_th))
        params.threshold_voltage_V = np.abs(v[th_idx])
    
    # Rollover parameters
    i_ro, v_ro, p_ro = extract_rollover_parameters(v, i, p)
    params.rollover_current_A = i_ro
    params.rollover_voltage_V = v_ro
    params.rollover_power_W = p_ro
    
    # Max power parameters
    p_max, i_at_max, v_at_max = extract_max_power_parameters(v, i, p)
    params.max_power_W = p_max
    params.current_at_max_power_A = i_at_max
    params.voltage_at_max_power_V = v_at_max
    
    # Power Conversion Efficiency (PCE)
    _, _, max_pce, i_at_max_pce, v_at_max_pce = calculate_power_conversion_efficiency(v, i, p)
    params.max_pce_pct = max_pce
    params.current_at_max_pce_A = i_at_max_pce
    params.voltage_at_max_pce_V = v_at_max_pce
    
    # V-I parameters
    n, I0, r2 = extract_ideality_factor(v, i)
    params.ideality_factor = n
    params.I0_A = I0
    params.fit_quality_r2 = r2
    
    # Series resistance
    Rs, Rd = extract_series_resistance(v, i)
    params.series_resistance_ohm = Rs
    params.differential_resistance_ohm = Rd
    
    # Additional parameters
    additional = extract_additional_parameters(v, i, p)
    params.wall_plug_efficiency = additional.get('wall_plug_efficiency_pct')
    params.knee_voltage_V = additional.get('knee_voltage_V')
    
    return params
