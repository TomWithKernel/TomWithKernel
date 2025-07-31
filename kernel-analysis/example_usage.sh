#!/bin/bash
# Example usage of the kernel crash analysis tools

echo "Linux Kernel Crash Analysis Tools - Example Usage"
echo "=================================================="
echo

# Check if crash utility is available
if command -v crash >/dev/null 2>&1; then
    echo "✓ crash utility is available"
else
    echo "! crash utility not found - install with: sudo apt-get install crash"
fi

# Check Python
if command -v python3 >/dev/null 2>&1; then
    echo "✓ Python 3 is available"
else
    echo "! Python 3 not found"
    exit 1
fi

echo
echo "Example commands:"
echo

echo "1. Get help for crash analysis:"
echo "   python3 analyze_crash.py --help-analysis"
echo

echo "2. Quick info about a vmcore file:"
echo "   python3 analyze_crash.py --quick-info --vmcore /path/to/vmcore"
echo

echo "3. Full analysis with vmlinux:"
echo "   python3 analyze_crash.py --vmcore /path/to/vmcore --vmlinux /path/to/vmlinux"
echo

echo "4. Save analysis to file:"
echo "   python3 analyze_crash.py --vmcore /path/to/vmcore --vmlinux /path/to/vmlinux -o report.txt"
echo

echo "Common vmcore locations:"
echo "- /var/crash/YYYY-MM-DD-HH:MM/vmcore"
echo "- /proc/vmcore (for currently running system)"
echo

echo "Common vmlinux locations:"
echo "- /boot/vmlinux-\$(uname -r)"
echo "- /usr/lib/debug/boot/vmlinux-\$(uname -r)"
echo

echo "For more information, run:"
echo "python3 analyze_crash.py --help-analysis"