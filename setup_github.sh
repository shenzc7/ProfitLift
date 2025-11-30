#!/bin/bash

# ProfitLift GitHub Setup Script
# Run this after creating the GitHub repository

echo "=== ProfitLift GitHub Setup ==="
echo "Setting up remote origin..."

git remote add origin https://github.com/shenzc7/ProfitLift.git 2>/dev/null || git remote set-url origin https://github.com/shenzc7/ProfitLift.git

echo "Switching to main branch..."
git branch -M main

echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ ProfitLift is now live on GitHub!"
echo "Repository: https://github.com/shenzc7/ProfitLift"
echo ""
echo "One-click Windows install command:"
echo 'powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/shenzc7/ProfitLift/main/scripts/windows/oneclick_setup.ps1 | iex"'
