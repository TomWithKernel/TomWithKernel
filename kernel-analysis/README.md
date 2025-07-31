# Linux Kernel Crash Analysis Tools

This directory contains tools for analyzing Linux kernel crash dumps (vmcore) and kernel images (vmlinux).

## Requirements

- Python 3.6+
- crash utility (for advanced analysis)
- file utility
- binutils (for objdump, readelf)

## Usage

### Basic Analysis

```bash
python3 analyze_crash.py --vmcore /path/to/vmcore --vmlinux /path/to/vmlinux
```

### Quick Info

```bash
python3 analyze_crash.py --quick-info --vmcore /path/to/vmcore
```

## Files

- `analyze_crash.py` - Main analysis script
- `crash_utils.py` - Utility functions for crash analysis
- `README.md` - This documentation

## Features

- Basic vmcore file validation
- vmlinux symbol extraction
- Crash context analysis
- Stack trace extraction
- Process list from crash dump
- Memory layout analysis

## Installation

No special installation required. Ensure Python 3.6+ is available and optionally install crash utility:

```bash
# Ubuntu/Debian
sudo apt-get install crash

# CentOS/RHEL
sudo yum install crash
```