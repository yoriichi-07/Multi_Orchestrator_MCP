#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Validate Vercel deployment configuration and dependencies
.DESCRIPTION
    Comprehensive validation script for Vercel serverless deployment of the Autonomous Software Foundry MCP Server
#>

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Color output functions
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }

Write-Host "Validating Vercel Deployment Configuration..." -ForegroundColor Blue
Write-Host ""

$validationPassed = $true

# 1. Check for required Vercel configuration files
Write-Info "Checking Vercel configuration files..."

$requiredFiles = @(
    "vercel.json",
    "requirements.txt",
    ".env.production.template",
    "src/main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Success "Found: $file"
    } else {
        Write-Error "Missing: $file"
        $validationPassed = $false
    }
}

# 2. Validate vercel.json configuration
Write-Info "Validating vercel.json configuration..."

if (Test-Path "vercel.json") {
    try {
        $vercelConfig = Get-Content "vercel.json" | ConvertFrom-Json
        
        # Check required properties
        if ($vercelConfig.version -eq 2) {
            Write-Success "Vercel version 2 configuration detected"
        } else {
            Write-Error "Invalid or missing Vercel version (should be 2)"
            $validationPassed = $false
        }
        
        if ($vercelConfig.builds -and $vercelConfig.builds[0].use -eq "@vercel/python") {
            Write-Success "Python runtime configured correctly"
        } else {
            Write-Error "Python runtime not configured correctly"
            $validationPassed = $false
        }
        
        if ($vercelConfig.routes) {
            Write-Success "Routes configured"
        } else {
            Write-Warning "No routes configured - may cause routing issues"
        }
        
    } catch {
        Write-Error "Invalid JSON in vercel.json: $($_.Exception.Message)"
        $validationPassed = $false
    }
} else {
    Write-Error "vercel.json not found"
    $validationPassed = $false
}

# 3. Check requirements.txt
Write-Info "Validating requirements.txt..."

if (Test-Path "requirements.txt") {
    $requirements = Get-Content "requirements.txt"
    
    $corePackages = @("fastapi", "uvicorn", "pydantic", "structlog")
    $foundPackages = @()
    
    foreach ($package in $corePackages) {
        $found = $requirements | Where-Object { $_ -match "^$package" }
        if ($found) {
            $foundPackages += $package
            Write-Success "Found dependency: $package"
        } else {
            Write-Error "Missing core dependency: $package"
            $validationPassed = $false
        }
    }
    
    Write-Success "Dependencies validation: $($foundPackages.Count)/$($corePackages.Count) core packages found"
} else {
    Write-Error "requirements.txt not found"
    $validationPassed = $false
}

# 4. Check for Docker files that should be removed
Write-Info "Checking for removed Docker files..."

$dockerFiles = @(
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore"
)

$foundDockerFiles = @()
foreach ($file in $dockerFiles) {
    if (Test-Path $file) {
        $foundDockerFiles += $file
        Write-Warning "Docker file still present: $file (should be removed for serverless deployment)"
    }
}

if ($foundDockerFiles.Count -eq 0) {
    Write-Success "All Docker files properly removed"
} else {
    Write-Warning "Consider removing Docker files: $($foundDockerFiles -join ', ')"
}

# 5. Check for Fly.io files that should be removed
Write-Info "Checking for removed Fly.io files..."

$flyFiles = @(
    "fly.toml",
    "Procfile",
    "runtime.txt"
)

$foundFlyFiles = @()
foreach ($file in $flyFiles) {
    if (Test-Path $file) {
        $foundFlyFiles += $file
        Write-Warning "Fly.io file still present: $file (should be removed for Vercel deployment)"
    }
}

if ($foundFlyFiles.Count -eq 0) {
    Write-Success "All Fly.io files properly removed"
} else {
    Write-Warning "Consider removing Fly.io files: $($foundFlyFiles -join ', ')"
}

# Final summary
Write-Host ""
Write-Host "Validation Summary" -ForegroundColor Blue
Write-Host "==================" -ForegroundColor Blue

if ($validationPassed) {
    Write-Success "All critical validations passed!"
    Write-Info "Your application is ready for Vercel deployment."
    Write-Host ""
    Write-Info "Next steps:"
    Write-Info "1. Set up external services (Database: Supabase/PlanetScale, Redis: Upstash)"
    Write-Info "2. Configure environment variables in Vercel dashboard"
    Write-Info "3. Run: vercel --prod"
    Write-Info "4. Follow the complete guide in VERCEL-DEPLOYMENT-GUIDE.md"
} else {
    Write-Error "Some validations failed. Please fix the issues above before deploying."
    exit 1
}

Write-Host ""
Write-Success "Validation completed successfully!"