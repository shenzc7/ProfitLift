@echo off
echo ========================================
echo    ProfitLift One-Click Installer
echo ========================================
echo.
echo This will install ProfitLift with all dependencies
echo and create a desktop shortcut.
echo.
echo Press any key to continue, or Ctrl+C to cancel...
pause >nul

powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/shenzc7/ProfitLift/main/scripts/windows/oneclick_setup.ps1 | iex"

echo.
echo Installation complete! Look for the ProfitLift icon on your desktop.
echo Press any key to exit...
pause >nul


