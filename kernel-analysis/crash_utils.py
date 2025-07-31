#!/usr/bin/env python3
"""
Linux Kernel Crash Analysis Utilities

This module provides utility functions for analyzing Linux kernel crash dumps
and vmlinux files.
"""

import os
import subprocess
import struct
import sys
from typing import Dict, List, Optional, Tuple


class VmcoreAnalyzer:
    """Analyzer for vmcore files"""
    
    def __init__(self, vmcore_path: str, vmlinux_path: Optional[str] = None):
        self.vmcore_path = vmcore_path
        self.vmlinux_path = vmlinux_path
        self.file_info = {}
        
    def validate_vmcore(self) -> bool:
        """Validate that the vmcore file exists and has basic structure"""
        if not os.path.exists(self.vmcore_path):
            print(f"Error: vmcore file not found: {self.vmcore_path}")
            return False
            
        try:
            # Check file size
            size = os.path.getsize(self.vmcore_path)
            if size < 1024:  # Should be at least 1KB
                print(f"Warning: vmcore file seems too small: {size} bytes")
                
            # Try to read ELF header
            with open(self.vmcore_path, 'rb') as f:
                elf_header = f.read(16)
                if len(elf_header) >= 4 and elf_header[:4] == b'\x7fELF':
                    print("✓ Valid ELF vmcore file detected")
                    return True
                else:
                    print("Warning: File doesn't appear to be a standard ELF vmcore")
                    return True  # Could still be valid, just different format
                    
        except Exception as e:
            print(f"Error reading vmcore file: {e}")
            return False
            
    def get_file_info(self) -> Dict[str, str]:
        """Get basic file information using file command"""
        try:
            result = subprocess.run(['file', self.vmcore_path], 
                                  capture_output=True, text=True)
            self.file_info['file_output'] = result.stdout.strip()
            
            # Get size
            size = os.path.getsize(self.vmcore_path)
            self.file_info['size'] = f"{size} bytes ({size / (1024*1024):.1f} MB)"
            
            return self.file_info
        except Exception as e:
            return {'error': str(e)}
            
    def analyze_with_crash(self) -> Optional[str]:
        """Analyze vmcore using crash utility if available"""
        if not self.vmlinux_path:
            return "vmlinux path required for crash analysis"
            
        try:
            # Check if crash utility is available
            subprocess.run(['crash', '--version'], capture_output=True, check=True)
            
            # Run basic crash analysis
            cmd = ['crash', '--no-panic', '--no-readline', 
                   self.vmlinux_path, self.vmcore_path]
            
            # Create a simple crash script
            crash_commands = "log\nps\nbt\nquit\n"
            
            result = subprocess.run(cmd, input=crash_commands, 
                                  capture_output=True, text=True, timeout=30)
            
            return result.stdout
            
        except subprocess.CalledProcessError:
            return "crash utility not available or failed to run"
        except subprocess.TimeoutExpired:
            return "crash analysis timed out"
        except Exception as e:
            return f"Error during crash analysis: {e}"


class VmlinuxAnalyzer:
    """Analyzer for vmlinux files"""
    
    def __init__(self, vmlinux_path: str):
        self.vmlinux_path = vmlinux_path
        
    def validate_vmlinux(self) -> bool:
        """Validate vmlinux file"""
        if not os.path.exists(self.vmlinux_path):
            print(f"Error: vmlinux file not found: {self.vmlinux_path}")
            return False
            
        try:
            # Check if it's an ELF file
            with open(self.vmlinux_path, 'rb') as f:
                elf_header = f.read(16)
                if len(elf_header) >= 4 and elf_header[:4] == b'\x7fELF':
                    print("✓ Valid ELF vmlinux file detected")
                    return True
                else:
                    print("Warning: File doesn't appear to be an ELF file")
                    return False
                    
        except Exception as e:
            print(f"Error reading vmlinux file: {e}")
            return False
            
    def get_kernel_version(self) -> Optional[str]:
        """Extract kernel version from vmlinux"""
        try:
            # Try to find version string using strings command
            result = subprocess.run(['strings', self.vmlinux_path], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'Linux version' in line:
                    return line.strip()
                    
            return None
            
        except Exception as e:
            return f"Error extracting version: {e}"
            
    def get_symbols(self, limit: int = 100) -> List[str]:
        """Get symbol information from vmlinux"""
        try:
            result = subprocess.run(['nm', self.vmlinux_path], 
                                  capture_output=True, text=True)
            
            symbols = []
            for line in result.stdout.split('\n')[:limit]:
                if line.strip():
                    symbols.append(line.strip())
                    
            return symbols
            
        except Exception as e:
            return [f"Error extracting symbols: {e}"]


def format_analysis_output(vmcore_info: Dict, vmlinux_info: Dict = None, 
                          crash_output: str = None) -> str:
    """Format analysis results for display"""
    output = []
    output.append("=" * 60)
    output.append("LINUX KERNEL CRASH ANALYSIS REPORT")
    output.append("=" * 60)
    output.append("")
    
    # Vmcore information
    output.append("VMCORE ANALYSIS:")
    output.append("-" * 20)
    for key, value in vmcore_info.items():
        output.append(f"{key}: {value}")
    output.append("")
    
    # Vmlinux information
    if vmlinux_info:
        output.append("VMLINUX ANALYSIS:")
        output.append("-" * 20)
        for key, value in vmlinux_info.items():
            if isinstance(value, list):
                output.append(f"{key}:")
                for item in value[:10]:  # Limit output
                    output.append(f"  {item}")
                if len(value) > 10:
                    output.append(f"  ... and {len(value) - 10} more")
            else:
                output.append(f"{key}: {value}")
        output.append("")
    
    # Crash analysis output
    if crash_output:
        output.append("CRASH UTILITY ANALYSIS:")
        output.append("-" * 25)
        output.append(crash_output)
        output.append("")
    
    output.append("=" * 60)
    return "\n".join(output)