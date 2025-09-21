#!/bin/bash
# Test script for runtime execution across Bash, Python, and Node.js

echo "Testing runtime execution..."

# Test Bash runtime
echo -n "Running Bash test: "
bash test_scripts/hello.sh

# Test Python runtime
echo -n "Running Python test: "
python test_scripts/hello.py

# Test Node.js runtime
echo -n "Running Node.js test: "
node test_scripts/hello.js

echo "All runtime tests completed!"