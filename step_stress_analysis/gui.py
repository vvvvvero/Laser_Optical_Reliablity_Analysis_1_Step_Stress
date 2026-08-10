#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI for step stress data analysis.

Author: Veronica GaoZhan
Date: February 2026
"""

import csv
import numpy as np
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QSplitter, QStatusBar, QScrollArea, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from .models import AnalysisResults
from .analysis_worker import AnalysisWorker
from .parameter_extractor import (
    calculate_slope_efficiency_vs_current, extract_threshold_max_slope,
    calculate_power_conversion_efficiency, extract_ideality_factor,
    extract_series_resistance, extract_max_power_parameters
)


class StepStressAnalysisGUI(QMainWindow):
    """Main GUI window for step stress data analysis"""
    
    def __init__(self):
        super().__init__()
        self.results: Optional[AnalysisResults] = None
        self.worker: Optional[AnalysisWorker] = None
        self.data_path: Optional[str] = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Step Stress Data Analysis - IVL Parameter Extraction — © Veronica GaoZhan")
        self.setMinimumSize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Plots
        plot_tabs = self.create_plot_tabs()
        splitter.addWidget(plot_tabs)
        
        # Right side: Parameters and Log
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([900, 500])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select a folder or file to analyze.")
        _copyright = QLabel("© Veronica GaoZhan — Step Stress Data Analysis")
        _copyright.setStyleSheet("color: gray; font-size: 9pt; padding-right: 6px;")
        self.status_bar.addPermanentWidget(_copyright)
    
    def create_control_panel(self) -> QGroupBox:
        """Create the top control panel"""
        group = QGroupBox("Data Selection")
        layout = QHBoxLayout(group)
        
        # Path input
        layout.addWidget(QLabel("Data Path:"))
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select folder or file...")
        self.path_edit.setMinimumWidth(400)
        layout.addWidget(self.path_edit)
        
        # Browse buttons
        btn_browse_folder = QPushButton("Browse Folder")
        btn_browse_folder.clicked.connect(self.browse_folder)
        layout.addWidget(btn_browse_folder)
        
        btn_browse_file = QPushButton("Browse File")
        btn_browse_file.clicked.connect(self.browse_file)
        layout.addWidget(btn_browse_file)
        
        layout.addSpacing(20)
        
        # Analyze button
        self.btn_analyze = QPushButton("⚡ Analyze Data")
        self.btn_analyze.setStyleSheet("font-weight: bold; padding: 8px 16px;")
        self.btn_analyze.clicked.connect(self.start_analysis)
        layout.addWidget(self.btn_analyze)
        
        # Export button
        self.btn_export = QPushButton("📥 Export Results")
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)
        
        layout.addStretch()
        
        return group
    
    def create_plot_tabs(self) -> QTabWidget:
        """Create the plot tabs"""
        tabs = QTabWidget()
        
        # Tab 1: IVL Plots
        ivl_widget = QWidget()
        ivl_layout = QVBoxLayout(ivl_widget)
        
        self.figure_ivl = Figure(figsize=(12, 10))
        self.canvas_ivl = FigureCanvas(self.figure_ivl)
        toolbar_ivl = NavigationToolbar(self.canvas_ivl, ivl_widget)
        
        ivl_layout.addWidget(toolbar_ivl)
        ivl_layout.addWidget(self.canvas_ivl)
        
        self.ax_iv = self.figure_ivl.add_subplot(221)
        self.ax_li = self.figure_ivl.add_subplot(222)
        self.ax_lv = self.figure_ivl.add_subplot(223)
        self.ax_semilog = self.figure_ivl.add_subplot(224)
        
        tabs.addTab(ivl_widget, "📊 IVL Characteristics")
        
        # Tab 2: Stress Monitoring
        stress_widget = QWidget()
        stress_layout = QVBoxLayout(stress_widget)
        
        self.figure_stress = Figure(figsize=(12, 8))
        self.canvas_stress = FigureCanvas(self.figure_stress)
        toolbar_stress = NavigationToolbar(self.canvas_stress, stress_widget)
        
        stress_layout.addWidget(toolbar_stress)
        stress_layout.addWidget(self.canvas_stress)
        
        self.ax_stress_current = self.figure_stress.add_subplot(211)
        self.ax_stress_voltage = self.figure_stress.add_subplot(212)
        
        tabs.addTab(stress_widget, "⚡ Stress Monitoring")
        
        # Tab 3: Relative Stress Data
        relative_widget = QWidget()
        relative_layout = QVBoxLayout(relative_widget)
        
        self.figure_relative = Figure(figsize=(12, 8))
        self.canvas_relative = FigureCanvas(self.figure_relative)
        toolbar_relative = NavigationToolbar(self.canvas_relative, relative_widget)
        
        relative_layout.addWidget(toolbar_relative)
        relative_layout.addWidget(self.canvas_relative)
        
        self.ax_rel_current = self.figure_relative.add_subplot(211)
        self.ax_rel_voltage = self.figure_relative.add_subplot(212)
        
        tabs.addTab(relative_widget, "📈 Relative Stress")
        
        # Tab 4: Parameter Trends
        trends_widget = QWidget()
        trends_layout = QVBoxLayout(trends_widget)
        
        self.figure_trends = Figure(figsize=(12, 10))
        self.canvas_trends = FigureCanvas(self.figure_trends)
        toolbar_trends = NavigationToolbar(self.canvas_trends, trends_widget)
        
        trends_layout.addWidget(toolbar_trends)
        trends_layout.addWidget(self.canvas_trends)
        
        tabs.addTab(trends_widget, "📉 Parameter Trends")
        
        # Tab 5: Fitting Examples
        fitting_widget = QWidget()
        fitting_layout = QVBoxLayout(fitting_widget)
        
        self.figure_fitting = Figure(figsize=(12, 10))
        self.canvas_fitting = FigureCanvas(self.figure_fitting)
        toolbar_fitting = NavigationToolbar(self.canvas_fitting, fitting_widget)
        
        fitting_layout.addWidget(toolbar_fitting)
        fitting_layout.addWidget(self.canvas_fitting)
        
        tabs.addTab(fitting_widget, "🔧 Fitting Examples")
        
        # Tab 6: PCE Analysis
        pce_widget = QWidget()
        pce_layout = QVBoxLayout(pce_widget)
        
        self.figure_pce = Figure(figsize=(12, 10))
        self.canvas_pce = FigureCanvas(self.figure_pce)
        toolbar_pce = NavigationToolbar(self.canvas_pce, pce_widget)
        
        pce_layout.addWidget(toolbar_pce)
        pce_layout.addWidget(self.canvas_pce)
        
        tabs.addTab(pce_widget, "⚡ PCE Analysis")
        
        return tabs
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with parameters table and log"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Parameter table
        param_group = QGroupBox("Extracted Parameters")
        param_layout = QVBoxLayout(param_group)
        
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(15)
        self.param_table.setHorizontalHeaderLabels([
            'Step', 'Stress', 'Ith (mA)', 'Vth (V)', 'Slope (mW/A)',
            'Pmax (μW)', 'I@Pmax (mA)', 'V@Pmax (V)',
            'PCE_max (%)', 'I@PCE (mA)', 'V@PCE (V)',
            'n', 'Rs (Ω)', 'Method', 'R²'
        ])
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.param_table.setAlternatingRowColors(True)
        param_layout.addWidget(self.param_table)
        
        layout.addWidget(param_group)
        
        # Log output
        log_group = QGroupBox("Analysis Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("font-family: Consolas, monospace; font-size: 10px;")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return widget
    
    def browse_folder(self):
        """Browse for a folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Data Folder",
            str(Path.cwd() / "results")
        )
        if folder:
            self.path_edit.setText(folder)
            self.data_path = folder
    
    def browse_file(self):
        """Browse for a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File",
            str(Path.cwd() / "results"),
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
            self.data_path = file_path
    
    def log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def start_analysis(self):
        """Start the analysis"""
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "No Path", "Please select a folder or file first.")
            return
        
        if not Path(path).exists():
            QMessageBox.warning(self, "Path Not Found", f"Path does not exist: {path}")
            return
        
        self.data_path = path
        self.log_text.clear()
        self.log(f"Starting analysis: {path}")
        
        self.btn_analyze.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.status_bar.showMessage("Analyzing...")
        
        # Start worker thread
        self.worker = AnalysisWorker(path)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_analysis_complete)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
    
    def on_analysis_complete(self, results: AnalysisResults):
        """Handle analysis completion"""
        self.results = results
        self.btn_analyze.setEnabled(True)
        self.btn_export.setEnabled(True)
        
        if not results.ivl_data and not results.stress_data:
            self.status_bar.showMessage("No data found!")
            QMessageBox.warning(self, "No Data", "No valid data could be loaded from the selected path.")
            return
        
        self.log(f"\n{'='*50}")
        self.log(f"Analysis complete!")
        self.log(f"  IVL datasets: {len(results.ivl_data)}")
        self.log(f"  Stress datasets: {len(results.stress_data)}")
        self.log(f"  Parameters extracted: {len(results.parameters)}")
        
        # Update all plots
        self.update_ivl_plots()
        self.update_stress_plots()
        self.update_relative_plots()
        self.update_trends_plots()
        self.update_fitting_plots()
        self.update_pce_plots()
        
        # Update parameter table
        self.update_parameter_table()
        
        self.status_bar.showMessage(
            f"Analysis complete: {len(results.ivl_data)} IVL, {len(results.stress_data)} stress datasets"
        )
    
    def on_analysis_error(self, error_msg: str):
        """Handle analysis error"""
        self.btn_analyze.setEnabled(True)
        self.log(f"ERROR: {error_msg}")
        self.status_bar.showMessage("Analysis failed!")
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n{error_msg}")
    
    def update_ivl_plots(self):
        """Update IVL characteristic plots"""
        if not self.results or not self.results.ivl_data:
            return
        
        # Clear all axes
        self.ax_iv.clear()
        self.ax_li.clear()
        self.ax_lv.clear()
        self.ax_semilog.clear()
        
        # Color mapping
        stress_levels = [ivl.stress_level for ivl in self.results.ivl_data]
        if len(set(stress_levels)) > 1:
            norm = Normalize(vmin=min(stress_levels), vmax=max(stress_levels))
        else:
            norm = Normalize(vmin=0, vmax=1)
        cmap = plt.cm.viridis
        
        for ivl in self.results.ivl_data:
            color = cmap(norm(ivl.stress_level))
            label = f"Step {ivl.step} ({ivl.stress_level:.3f})"
            
            # I-V plot
            self.ax_iv.plot(ivl.voltage, ivl.current * 1e3, '-', 
                           color=color, linewidth=1.5, label=label)
            
            # L-I plot
            self.ax_li.plot(ivl.current * 1e3, ivl.optical_power * 1e6, '-',
                           color=color, linewidth=1.5, label=label)
            
            # L-V plot
            self.ax_lv.plot(ivl.voltage, ivl.optical_power * 1e6, '-',
                           color=color, linewidth=1.5, label=label)
            
            # Semi-log I-V plot
            i_positive = np.abs(ivl.current)
            i_positive[i_positive < 1e-15] = 1e-15
            self.ax_semilog.semilogy(ivl.voltage, i_positive, '-',
                                    color=color, linewidth=1.5, label=label)
        
        self.ax_iv.set_xlabel('Voltage (V)')
        self.ax_iv.set_ylabel('Current (mA)')
        self.ax_iv.set_title('I-V Characteristics')
        self.ax_iv.grid(True, alpha=0.3)
        
        self.ax_li.set_xlabel('Current (mA)')
        self.ax_li.set_ylabel('Optical Power (μW)')
        self.ax_li.set_title('L-I Characteristics')
        self.ax_li.grid(True, alpha=0.3)
        
        self.ax_lv.set_xlabel('Voltage (V)')
        self.ax_lv.set_ylabel('Optical Power (μW)')
        self.ax_lv.set_title('L-V Characteristics')
        self.ax_lv.grid(True, alpha=0.3)
        
        self.ax_semilog.set_xlabel('Voltage (V)')
        self.ax_semilog.set_ylabel('Current (A)')
        self.ax_semilog.set_title('Semi-log I-V (for ideality factor)')
        self.ax_semilog.grid(True, alpha=0.3)
        
        # Add legend if few curves
        if len(self.results.ivl_data) <= 10:
            self.ax_iv.legend(fontsize=7, loc='best')
        
        self.figure_ivl.tight_layout()
        self.canvas_ivl.draw()
    
    def update_stress_plots(self):
        """Update stress monitoring plots"""
        self.ax_stress_current.clear()
        self.ax_stress_voltage.clear()
        
        if not self.results or not self.results.stress_data:
            self.ax_stress_current.set_title('No Stress Data')
            self.canvas_stress.draw()
            return
        
        cmap = plt.cm.tab10
        
        for idx, stress in enumerate(self.results.stress_data):
            color = cmap(idx % 10)
            label = f"Step {stress.step}"
            
            self.ax_stress_current.plot(stress.time, stress.current * 1e3, '-',
                                        color=color, linewidth=1, label=label)
            self.ax_stress_voltage.plot(stress.time, stress.voltage, '-',
                                        color=color, linewidth=1, label=label)
        
        self.ax_stress_current.set_ylabel('Current (mA)')
        self.ax_stress_current.set_title('Current During Stress')
        self.ax_stress_current.grid(True, alpha=0.3)
        self.ax_stress_current.legend(loc='best', fontsize=8)
        
        self.ax_stress_voltage.set_xlabel('Time (s)')
        self.ax_stress_voltage.set_ylabel('Voltage (V)')
        self.ax_stress_voltage.set_title('Voltage During Stress')
        self.ax_stress_voltage.grid(True, alpha=0.3)
        
        self.figure_stress.tight_layout()
        self.canvas_stress.draw()
    
    def update_relative_plots(self):
        """Update relative stress data plots"""
        self.ax_rel_current.clear()
        self.ax_rel_voltage.clear()
        
        if not self.results or not self.results.stress_data:
            self.ax_rel_current.set_title('No Stress Data')
            self.canvas_relative.draw()
            return
        
        cmap = plt.cm.tab10
        
        for idx, stress in enumerate(self.results.stress_data):
            color = cmap(idx % 10)
            label = f"Step {stress.step}"
            
            if len(stress.current) > 2:
                ref_current = stress.current[1] if stress.current[1] != 0 else stress.current[0]
                ref_voltage = stress.voltage[1] if stress.voltage[1] != 0 else stress.voltage[0]
                
                rel_current = stress.current / ref_current if ref_current != 0 else stress.current
                rel_voltage = stress.voltage / ref_voltage if ref_voltage != 0 else stress.voltage
                
                self.ax_rel_current.plot(stress.time, rel_current, '-',
                                         color=color, linewidth=1, label=label)
                self.ax_rel_voltage.plot(stress.time, rel_voltage, '-',
                                         color=color, linewidth=1, label=label)
        
        self.ax_rel_current.set_ylabel('Relative Current (I/I₀)')
        self.ax_rel_current.set_title('Relative Current During Stress (normalized to 2nd point)')
        self.ax_rel_current.grid(True, alpha=0.3)
        self.ax_rel_current.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
        self.ax_rel_current.legend(loc='best', fontsize=8)
        
        self.ax_rel_voltage.set_xlabel('Time (s)')
        self.ax_rel_voltage.set_ylabel('Relative Voltage (V/V₀)')
        self.ax_rel_voltage.set_title('Relative Voltage During Stress (normalized to 2nd point)')
        self.ax_rel_voltage.grid(True, alpha=0.3)
        self.ax_rel_voltage.axhline(y=1.0, color='k', linestyle='--', alpha=0.5)
        
        self.figure_relative.tight_layout()
        self.canvas_relative.draw()
    
    def update_trends_plots(self):
        """Update parameter trends plots"""
        self.figure_trends.clear()
        
        if not self.results or not self.results.parameters:
            ax = self.figure_trends.add_subplot(111)
            ax.set_title('No Parameters Extracted')
            self.canvas_trends.draw()
            return
        
        axes = self.figure_trends.subplots(2, 3)
        
        # Threshold current trend
        i_th = [p.threshold_current_A for p in self.results.parameters if p.threshold_current_A]
        s_th = [p.stress_level for p in self.results.parameters if p.threshold_current_A]
        if i_th:
            axes[0, 0].plot(s_th, np.array(i_th) * 1e3, 'bo-', markersize=8)
            axes[0, 0].set_xlabel('Stress Level')
            axes[0, 0].set_ylabel('Threshold Current (mA)')
            axes[0, 0].set_title('Ith vs Stress')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Max power trend
        p_max = [p.max_power_W for p in self.results.parameters if p.max_power_W]
        s_max = [p.stress_level for p in self.results.parameters if p.max_power_W]
        if p_max:
            axes[0, 1].plot(s_max, np.array(p_max) * 1e6, 'rs-', markersize=8)
            axes[0, 1].set_xlabel('Stress Level')
            axes[0, 1].set_ylabel('Max Power (μW)')
            axes[0, 1].set_title('Pmax vs Stress')
            axes[0, 1].grid(True, alpha=0.3)
        
        # Slope efficiency trend
        se = [p.slope_efficiency_W_A for p in self.results.parameters if p.slope_efficiency_W_A]
        s_se = [p.stress_level for p in self.results.parameters if p.slope_efficiency_W_A]
        if se:
            axes[0, 2].plot(s_se, np.array(se) * 1e3, 'g^-', markersize=8)
            axes[0, 2].set_xlabel('Stress Level')
            axes[0, 2].set_ylabel('Slope Efficiency (mW/A)')
            axes[0, 2].set_title('Slope Eff vs Stress')
            axes[0, 2].grid(True, alpha=0.3)
        
        # Series resistance trend
        Rs = [p.series_resistance_ohm for p in self.results.parameters if p.series_resistance_ohm]
        s_Rs = [p.stress_level for p in self.results.parameters if p.series_resistance_ohm]
        if Rs:
            axes[1, 0].plot(s_Rs, Rs, 'mo-', markersize=8)
            axes[1, 0].set_xlabel('Stress Level')
            axes[1, 0].set_ylabel('Series Resistance (Ω)')
            axes[1, 0].set_title('Rs vs Stress')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Ideality factor trend
        n = [p.ideality_factor for p in self.results.parameters if p.ideality_factor]
        s_n = [p.stress_level for p in self.results.parameters if p.ideality_factor]
        if n:
            axes[1, 1].plot(s_n, n, 'cv-', markersize=8)
            axes[1, 1].set_xlabel('Stress Level')
            axes[1, 1].set_ylabel('Ideality Factor (n)')
            axes[1, 1].set_title('n vs Stress')
            axes[1, 1].grid(True, alpha=0.3)
        
        # Wall-plug efficiency trend
        wpe = [p.wall_plug_efficiency for p in self.results.parameters if p.wall_plug_efficiency]
        s_wpe = [p.stress_level for p in self.results.parameters if p.wall_plug_efficiency]
        if wpe:
            axes[1, 2].plot(s_wpe, wpe, 'kd-', markersize=8)
            axes[1, 2].set_xlabel('Stress Level')
            axes[1, 2].set_ylabel('WPE (%)')
            axes[1, 2].set_title('WPE vs Stress')
            axes[1, 2].grid(True, alpha=0.3)
        
        self.figure_trends.tight_layout()
        self.canvas_trends.draw()
    
    def update_fitting_plots(self):
        """Update fitting example plots"""
        self.figure_fitting.clear()
        
        if not self.results or not self.results.ivl_data:
            ax = self.figure_fitting.add_subplot(111)
            ax.set_title('No IVL Data for Fitting')
            self.canvas_fitting.draw()
            return
        
        ivl = self.results.ivl_data[0]  # Use baseline measurement
        v, i, p = ivl.voltage, ivl.current, ivl.optical_power
        
        axes = self.figure_fitting.subplots(2, 3)
        
        # 1. L-I with threshold fit
        ax = axes[0, 0]
        i_mA = np.abs(i) * 1e3
        p_uW = np.abs(p) * 1e6
        ax.plot(i_mA, p_uW, 'b.-', label='Data', markersize=4)
        
        # Use max slope method for threshold extraction
        i_th, slope, i_arr, slope_arr = extract_threshold_max_slope(i, p)
        if i_th is not None and slope is not None:
            i_fit_range = np.linspace(i_th * 0.9, np.max(np.abs(i)) * 0.9, 100)
            p_fit = slope * (i_fit_range - i_th)
            p_fit[p_fit < 0] = 0
            ax.plot(i_fit_range * 1e3, p_fit * 1e6, 'r--', linewidth=2, 
                   label=f'Fit: Ith={i_th*1e3:.3f}mA')
            ax.axvline(x=i_th * 1e3, color='g', linestyle=':', alpha=0.7, label='Threshold')
        elif i_th is not None:
            ax.axvline(x=i_th * 1e3, color='g', linestyle=':', alpha=0.7, 
                      label=f'Ith={i_th*1e3:.3f}mA')
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Optical Power (μW)')
        ax.set_title('L-I with Threshold Current Fit')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # 2. Slope Efficiency (dP/dI) vs Current
        ax = axes[0, 1]
        if len(i_arr) > 0 and len(slope_arr) > 0:
            ax.plot(i_arr * 1e3, slope_arr * 1e3, 'b.-', label='dP/dI', markersize=4)
            
            max_slope_idx = np.argmax(slope_arr)
            ax.plot(i_arr[max_slope_idx] * 1e3, slope_arr[max_slope_idx] * 1e3, 'ro', 
                   markersize=10, label=f'Max: {slope_arr[max_slope_idx]*1e3:.2f} mW/A')
            
            if i_th is not None:
                ax.axvline(x=i_th * 1e3, color='g', linestyle=':', alpha=0.7, 
                          label=f'Ith={i_th*1e3:.3f}mA')
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Slope Efficiency (mW/A)')
        ax.set_title('Slope Efficiency vs Current')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # 3. V-I with ideality factor fit
        ax = axes[0, 2]
        i_abs = np.abs(i)
        valid_mask = i_abs > 1e-12
        
        ax.semilogy(v[valid_mask], i_abs[valid_mask], 'b.-', label='Data', markersize=4)
        
        n, I0, r2 = extract_ideality_factor(v, i)
        if n is not None and I0 is not None:
            Vt = 0.026
            v_fit_range = np.linspace(0.6, 0.9, 100)
            i_fit = I0 * np.exp(v_fit_range / (n * Vt))
            valid_fit = i_fit < np.max(i_abs) * 2
            ax.semilogy(v_fit_range[valid_fit], i_fit[valid_fit], 'r--', linewidth=2,
                       label=f'Exp fit (n={n:.2f}, R²={r2:.3f})')
        
        ax.set_xlabel('Voltage (V)')
        ax.set_ylabel('Current (A)')
        ax.set_title('Semi-log I-V (Ideality Factor)')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # 4. V-I linear region with series resistance fit
        ax = axes[1, 0]
        ax.plot(i * 1e3, v, 'b.-', label='Data', markersize=4)
        
        Rs, Rd = extract_series_resistance(v, i)
        if Rs is not None:
            linear_mask = (np.abs(i) > 0.3 * np.max(np.abs(i))) & (np.abs(i) < 0.9 * np.max(np.abs(i)))
            if np.any(linear_mask):
                coeffs = np.polyfit(i[linear_mask], v[linear_mask], 1)
                i_fit_range = np.linspace(np.max(np.abs(i)) * 0.3, np.max(np.abs(i)) * 0.95, 100)
                v_fit = np.polyval(coeffs, i_fit_range)
                ax.plot(i_fit_range * 1e3, v_fit, 'r--', linewidth=2,
                       label=f'Linear fit (Rs={Rs:.1f} Ω)')
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('V-I with Series Resistance Fit')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # 5. L-V plot with max power markers
        ax = axes[1, 1]
        ax.plot(v, p_uW, 'b.-', label='Data', markersize=4)
        
        p_max, i_at_max, v_at_max = extract_max_power_parameters(v, i, p)
        ax.axhline(y=p_max * 1e6, color='r', linestyle='--', alpha=0.5, 
                  label=f'Max: {p_max*1e6:.2f} μW')
        ax.axvline(x=v_at_max, color='g', linestyle=':', alpha=0.7, 
                  label=f'V: {v_at_max:.3f} V')
        ax.plot(v_at_max, p_max * 1e6, 'ro', markersize=10, label='Max point')
        
        ax.set_xlabel('Voltage (V)')
        ax.set_ylabel('Optical Power (μW)')
        ax.set_title('L-V with Max Power Markers')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        # 6. Slope Efficiency vs Current for ALL measurements
        ax = axes[1, 2]
        stress_levels = [ivl.stress_level for ivl in self.results.ivl_data]
        if len(set(stress_levels)) > 1:
            norm = Normalize(vmin=min(stress_levels), vmax=max(stress_levels))
        else:
            norm = Normalize(vmin=0, vmax=1)
        cmap = plt.cm.viridis
        
        for ivl in self.results.ivl_data:
            color = cmap(norm(ivl.stress_level))
            label = f"Step {ivl.step}"
            
            i_arr, slope_arr = calculate_slope_efficiency_vs_current(ivl.current, ivl.optical_power)
            if len(i_arr) > 0:
                ax.plot(i_arr * 1e3, slope_arr * 1e3, '-', color=color, linewidth=1.5, label=label)
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('Slope Efficiency (mW/A)')
        ax.set_title('Slope Efficiency vs Current (All Steps)')
        ax.grid(True, alpha=0.3)
        if len(self.results.ivl_data) <= 10:
            ax.legend(fontsize=6, loc='best')
        
        self.figure_fitting.tight_layout()
        self.canvas_fitting.draw()
    
    def update_pce_plots(self):
        """Update Power Conversion Efficiency plots"""
        self.figure_pce.clear()
        
        if not self.results or not self.results.ivl_data:
            ax = self.figure_pce.add_subplot(111)
            ax.set_title('No IVL Data for PCE Analysis')
            self.canvas_pce.draw()
            return
        
        axes = self.figure_pce.subplots(2, 2)
        
        # Color mapping
        stress_levels = [ivl.stress_level for ivl in self.results.ivl_data]
        if len(set(stress_levels)) > 1:
            norm = Normalize(vmin=min(stress_levels), vmax=max(stress_levels))
        else:
            norm = Normalize(vmin=0, vmax=1)
        cmap = plt.cm.viridis
        
        # 1. PCE vs Current for all measurements
        ax = axes[0, 0]
        for ivl in self.results.ivl_data:
            color = cmap(norm(ivl.stress_level))
            label = f"Step {ivl.step}"
            
            i_arr, pce_arr, max_pce, i_max, v_max = calculate_power_conversion_efficiency(
                ivl.voltage, ivl.current, ivl.optical_power
            )
            
            if len(i_arr) > 0:
                ax.plot(i_arr * 1e3, pce_arr, '-', color=color, linewidth=1.5, label=label)
                ax.plot(i_max * 1e3, max_pce, 'o', color=color, markersize=8)
        
        ax.set_xlabel('Current (mA)')
        ax.set_ylabel('PCE (%)')
        ax.set_title('Power Conversion Efficiency vs Current')
        ax.grid(True, alpha=0.3)
        if len(self.results.ivl_data) <= 10:
            ax.legend(fontsize=7, loc='best')
        
        # 2. PCE vs Voltage
        ax = axes[0, 1]
        for ivl in self.results.ivl_data:
            color = cmap(norm(ivl.stress_level))
            
            v_abs = np.abs(ivl.voltage)
            i_abs = np.abs(ivl.current)
            p_abs = np.abs(ivl.optical_power)
            p_elec = v_abs * i_abs
            valid = p_elec > 1e-15
            
            if np.any(valid):
                pce = 100 * p_abs[valid] / p_elec[valid]
                ax.plot(v_abs[valid], pce, '-', color=color, linewidth=1.5)
        
        ax.set_xlabel('Voltage (V)')
        ax.set_ylabel('PCE (%)')
        ax.set_title('Power Conversion Efficiency vs Voltage')
        ax.grid(True, alpha=0.3)
        
        # 3. Max PCE vs Stress Level
        ax = axes[1, 0]
        max_pces = [p.max_pce_pct for p in self.results.parameters if p.max_pce_pct]
        stress_lvls = [p.stress_level for p in self.results.parameters if p.max_pce_pct]
        
        if max_pces:
            ax.plot(stress_lvls, max_pces, 'ro-', markersize=8, linewidth=2)
            ax.set_xlabel('Stress Level')
            ax.set_ylabel('Maximum PCE (%)')
            ax.set_title('Maximum PCE vs Stress Level')
            ax.grid(True, alpha=0.3)
        
        # 4. Current at Max PCE vs Stress Level
        ax = axes[1, 1]
        i_at_pce = [p.current_at_max_pce_A for p in self.results.parameters if p.current_at_max_pce_A]
        stress_lvls2 = [p.stress_level for p in self.results.parameters if p.current_at_max_pce_A]
        
        if i_at_pce:
            ax.plot(stress_lvls2, np.array(i_at_pce) * 1e3, 'bs-', markersize=8, linewidth=2)
            ax.set_xlabel('Stress Level')
            ax.set_ylabel('Current at Max PCE (mA)')
            ax.set_title('Optimal Current vs Stress Level')
            ax.grid(True, alpha=0.3)
        
        self.figure_pce.tight_layout()
        self.canvas_pce.draw()
    
    def update_parameter_table(self):
        """Update the parameter table"""
        if not self.results or not self.results.parameters:
            self.param_table.setRowCount(0)
            return
        
        self.param_table.setRowCount(len(self.results.parameters))
        
        for row, p in enumerate(self.results.parameters):
            items = [
                str(p.step),
                f"{p.stress_level:.4f}",
                f"{p.threshold_current_A * 1e3:.4f}" if p.threshold_current_A else "-",
                f"{p.threshold_voltage_V:.4f}" if p.threshold_voltage_V else "-",
                f"{p.slope_efficiency_W_A * 1e3:.4f}" if p.slope_efficiency_W_A else "-",
                f"{p.max_power_W * 1e6:.4f}" if p.max_power_W else "-",
                f"{p.current_at_max_power_A * 1e3:.4f}" if p.current_at_max_power_A else "-",
                f"{p.voltage_at_max_power_V:.4f}" if p.voltage_at_max_power_V else "-",
                f"{p.max_pce_pct:.2f}" if p.max_pce_pct else "-",
                f"{p.current_at_max_pce_A * 1e3:.4f}" if p.current_at_max_pce_A else "-",
                f"{p.voltage_at_max_pce_V:.4f}" if p.voltage_at_max_pce_V else "-",
                f"{p.ideality_factor:.4f}" if p.ideality_factor else "-",
                f"{p.series_resistance_ohm:.2f}" if p.series_resistance_ohm else "-",
                p.threshold_method[:10] if p.threshold_method else "-",
                f"{p.fit_quality_r2:.4f}" if p.fit_quality_r2 else "-"
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.param_table.setItem(row, col, item)
    
    def export_results(self):
        """Export results to CSV"""
        if not self.results or not self.results.parameters:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return
        
        # Get output file path
        default_name = "extracted_parameters.csv"
        if self.data_path:
            data_path = Path(self.data_path)
            if data_path.is_dir():
                default_path = data_path / default_name
            else:
                default_path = data_path.parent / default_name
        else:
            default_path = Path.cwd() / default_name
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Parameters",
            str(default_path),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            fieldnames = [
                'Step', 'Stress_Level',
                'Threshold_Current_mA', 'Threshold_Voltage_V', 'Slope_Efficiency_mW_A', 'Threshold_Method',
                'Rollover_Current_mA', 'Rollover_Voltage_V', 'Rollover_Power_uW',
                'Max_Power_uW', 'Current_at_Max_Power_mA', 'Voltage_at_Max_Power_V',
                'Max_PCE_pct', 'Current_at_Max_PCE_mA', 'Voltage_at_Max_PCE_V',
                'Ideality_Factor', 'I0_A', 'Series_Resistance_Ohm', 'Differential_Resistance_Ohm',
                'Wall_Plug_Efficiency_pct', 'Knee_Voltage_V', 'Fit_Quality_R2'
            ]
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for p in self.results.parameters:
                    row = {
                        'Step': p.step,
                        'Stress_Level': p.stress_level,
                        'Threshold_Current_mA': f"{p.threshold_current_A * 1e3:.6f}" if p.threshold_current_A else '',
                        'Threshold_Voltage_V': f"{p.threshold_voltage_V:.6f}" if p.threshold_voltage_V else '',
                        'Slope_Efficiency_mW_A': f"{p.slope_efficiency_W_A * 1e3:.6f}" if p.slope_efficiency_W_A else '',
                        'Threshold_Method': p.threshold_method if p.threshold_method else '',
                        'Rollover_Current_mA': f"{p.rollover_current_A * 1e3:.6f}" if p.rollover_current_A else '',
                        'Rollover_Voltage_V': f"{p.rollover_voltage_V:.6f}" if p.rollover_voltage_V else '',
                        'Rollover_Power_uW': f"{p.rollover_power_W * 1e6:.6f}" if p.rollover_power_W else '',
                        'Max_Power_uW': f"{p.max_power_W * 1e6:.6f}" if p.max_power_W else '',
                        'Current_at_Max_Power_mA': f"{p.current_at_max_power_A * 1e3:.6f}" if p.current_at_max_power_A else '',
                        'Voltage_at_Max_Power_V': f"{p.voltage_at_max_power_V:.6f}" if p.voltage_at_max_power_V else '',
                        'Max_PCE_pct': f"{p.max_pce_pct:.4f}" if p.max_pce_pct else '',
                        'Current_at_Max_PCE_mA': f"{p.current_at_max_pce_A * 1e3:.6f}" if p.current_at_max_pce_A else '',
                        'Voltage_at_Max_PCE_V': f"{p.voltage_at_max_pce_V:.6f}" if p.voltage_at_max_pce_V else '',
                        'Ideality_Factor': f"{p.ideality_factor:.4f}" if p.ideality_factor else '',
                        'I0_A': f"{p.I0_A:.4e}" if p.I0_A else '',
                        'Series_Resistance_Ohm': f"{p.series_resistance_ohm:.4f}" if p.series_resistance_ohm else '',
                        'Differential_Resistance_Ohm': f"{p.differential_resistance_ohm:.4f}" if p.differential_resistance_ohm else '',
                        'Wall_Plug_Efficiency_pct': f"{p.wall_plug_efficiency:.4f}" if p.wall_plug_efficiency else '',
                        'Knee_Voltage_V': f"{p.knee_voltage_V:.6f}" if p.knee_voltage_V else '',
                        'Fit_Quality_R2': f"{p.fit_quality_r2:.4f}" if p.fit_quality_r2 else ''
                    }
                    writer.writerow(row)
            
            self.log(f"\nExported parameters to: {file_path}")
            self.status_bar.showMessage(f"Exported to: {file_path}")
            QMessageBox.information(self, "Export Complete", f"Parameters exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{e}")
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(2000)
        event.accept()
