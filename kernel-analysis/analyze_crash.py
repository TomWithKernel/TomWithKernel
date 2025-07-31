#!/usr/bin/env python3
"""
Linux Kernel Crash Analysis Tool

This script analyzes Linux kernel crash dumps (vmcore) and kernel images (vmlinux)
to help diagnose kernel panics and crashes.

Usage:
    python3 analyze_crash.py --vmcore /path/to/vmcore [--vmlinux /path/to/vmlinux]
    python3 analyze_crash.py --quick-info --vmcore /path/to/vmcore
"""

import argparse
import sys
import os
from crash_utils import VmcoreAnalyzer, VmlinuxAnalyzer, format_analysis_output


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Linux kernel crash dumps and vmlinux files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --vmcore /var/crash/vmcore --vmlinux /boot/vmlinux-5.4.0
  %(prog)s --quick-info --vmcore /var/crash/vmcore
  %(prog)s --help-analysis
        """
    )
    
    parser.add_argument('--vmcore',
                        help='Path to vmcore file')
    parser.add_argument('--vmlinux', 
                        help='Path to vmlinux file (optional but recommended)')
    parser.add_argument('--quick-info', action='store_true',
                        help='Show only basic file information')
    parser.add_argument('--output', '-o',
                        help='Output file for analysis results')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--help-analysis', action='store_true',
                        help='Show help for kernel crash analysis')
    
    args = parser.parse_args()
    
    if args.help_analysis:
        show_analysis_help()
        return 0
    
    if not args.vmcore:
        parser.error("--vmcore is required (unless using --help-analysis)")
    
    # Validate input files
    if not os.path.exists(args.vmcore):
        print(f"Error: vmcore file not found: {args.vmcore}")
        return 1
        
    if args.vmlinux and not os.path.exists(args.vmlinux):
        print(f"Error: vmlinux file not found: {args.vmlinux}")
        return 1
    
    if args.verbose:
        print("Starting kernel crash analysis...")
        print(f"vmcore: {args.vmcore}")
        if args.vmlinux:
            print(f"vmlinux: {args.vmlinux}")
    
    # Analyze vmcore
    print("Analyzing vmcore file...")
    vmcore_analyzer = VmcoreAnalyzer(args.vmcore, args.vmlinux)
    
    if not vmcore_analyzer.validate_vmcore():
        print("Failed to validate vmcore file")
        return 1
    
    vmcore_info = vmcore_analyzer.get_file_info()
    
    if args.quick_info:
        print("\nQuick Information:")
        for key, value in vmcore_info.items():
            print(f"{key}: {value}")
        return 0
    
    # Analyze vmlinux if provided
    vmlinux_info = None
    if args.vmlinux:
        print("Analyzing vmlinux file...")
        vmlinux_analyzer = VmlinuxAnalyzer(args.vmlinux)
        
        if vmlinux_analyzer.validate_vmlinux():
            vmlinux_info = {}
            version = vmlinux_analyzer.get_kernel_version()
            if version:
                vmlinux_info['kernel_version'] = version
                
            symbols = vmlinux_analyzer.get_symbols(50)  # Get first 50 symbols
            vmlinux_info['symbols_sample'] = symbols
    
    # Run crash analysis if both files are available
    crash_output = None
    if args.vmlinux:
        print("Running crash utility analysis...")
        crash_output = vmcore_analyzer.analyze_with_crash()
    
    # Format and display results
    analysis_report = format_analysis_output(vmcore_info, vmlinux_info, crash_output)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(analysis_report)
            print(f"Analysis results written to: {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            print("Displaying results to console instead:")
            print(analysis_report)
    else:
        print(analysis_report)
    
    return 0


def show_analysis_help():
    """Show detailed help for kernel crash analysis"""
    help_text = """
LINUX KERNEL CRASH ANALYSIS HELP
=================================

This tool helps analyze Linux kernel crash dumps to diagnose system failures.

WHAT YOU NEED:
--------------
1. vmcore file - The memory dump created when kernel crashed
   Usually found in: /var/crash/ or /proc/vmcore
   
2. vmlinux file - The uncompressed kernel image with debug symbols
   Usually found in: /boot/ or /usr/lib/debug/boot/
   Should match the kernel version that crashed

TYPICAL WORKFLOW:
-----------------
1. Identify the crash files:
   - Find vmcore in /var/crash/YYYY-MM-DD-HH:MM/vmcore
   - Find matching vmlinux in /boot/vmlinux-<version> or 
     /usr/lib/debug/boot/vmlinux-<version>

2. Run basic analysis:
   python3 analyze_crash.py --vmcore /path/to/vmcore --vmlinux /path/to/vmlinux

3. Review the output for:
   - Crash context and backtrace
   - Running processes at time of crash
   - Kernel log messages
   - Memory layout

UNDERSTANDING RESULTS:
----------------------
- Backtrace shows the call stack when crash occurred
- Process list shows what was running
- Log messages may indicate the trigger
- Symbols help identify exact functions involved

TROUBLESHOOTING:
----------------
- If vmlinux symbols don't match: verify kernel version matches
- If crash utility fails: install crash package or use quick-info mode
- For compressed dumps: decompress vmcore first

EXAMPLE COMMANDS:
-----------------
# Basic analysis with both files
python3 analyze_crash.py --vmcore /var/crash/vmcore --vmlinux /boot/vmlinux-5.4.0

# Quick file info only
python3 analyze_crash.py --quick-info --vmcore /var/crash/vmcore

# Save results to file
python3 analyze_crash.py --vmcore /var/crash/vmcore --vmlinux /boot/vmlinux-5.4.0 -o crash_report.txt
"""
    print(help_text)


if __name__ == '__main__':
    sys.exit(main())