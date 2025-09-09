@echo off
echo Testing authentication validation with demo mode...
echo.

rem Set environment variables
set DESCOPE_DEMO_MODE=true

echo Running validation script...
python scripts/validate_auth.py K32Rp16ZalqBZSInaW3GNWSwjRfhyvUwGRiMr3bOmJL4zCnO0qP80FDXfN5b1mDQIVnuvdo

pause