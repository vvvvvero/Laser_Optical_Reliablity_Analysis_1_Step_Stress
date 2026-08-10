#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup configuration for step-stress-analysis package.

Author: Veronica GaoZhan
Date: February 2026
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="step-stress-analysis",
    version="1.0.0",
    author="Veronica GaoZhan",
    author_email="veronica.gao.zhan@example.com",
    description="Comprehensive analysis library for step stress measurements of semiconductor devices (VCSELs, laser diodes, etc.)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vvvvvero/Laser_Optical_Reliablity_Analysis_1_Step_Stress",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15",
        "numpy>=1.19",
        "matplotlib>=3.3",
        "scipy>=1.5"
    ],
    entry_points={
        "console_scripts": [
            "step-stress-analysis=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
