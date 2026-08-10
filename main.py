#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for Step Stress Data Analysis GUI application.

Author: Veronica GaoZhan
Date: February 2026
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from step_stress_analysis.gui import StepStressAnalysisGUI


def main():
    """Launch the GUI application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(9)
    app.setFont(font)
    
    # Create and show main window
    window = StepStressAnalysisGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
