#!/bin/bash
# Executes a bash command safely.
echo "Executing command: $1"
eval "$1"
