# test-deployment-simple.ps1 - Simplified deployment validation script

param(
    [switch]$SkipTests = $false,
    [switch]$SkipLinting = $false
)

$ErrorActionPreference = "Continue"

function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    switch ($Type) {
        "OK" { Write-Host "[OK] $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "WARN" { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
        default { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
    }
}

function Test-Prerequisites {
    Write-Status "Checking prerequisites..." "INFO"
    
    $issues = @()
    
    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Python: $pythonVersion" "OK"
        } else {
            $issues += "Python not found or not working"
        }
    }
    catch {
        $issues += "Python not found"
    }
    
    # Check Poetry
    try {
        $poetryVersion = & poetry --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Poetry: $poetryVersion" "OK"
        } else {
            $issues += "Poetry not found or not working"
        }
    }
    catch {
        $issues += "Poetry not found"
    }
    
    # Check required files
    $requiredFiles = @(
        "pyproject.toml",
        "vercel.json",
        ".env.production.template",
        "src/main.py"
    )
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Status "Found: $file" "OK"
        } else {
            $issues += "Missing file: $file"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-Status "Prerequisites check failed:" "ERROR"
        foreach ($issue in $issues) {
            Write-Status "  - $issue" "ERROR"
        }
        return $false
    }
    
    Write-Status "All prerequisites satisfied" "OK"
    return $true
}

function Test-ProjectStructure {
    Write-Status "Validating project structure..." "INFO"
    
    $requiredDirs = @(
        "src",
        "scripts"
    )
    
    $missingDirs = @()
    
    foreach ($dir in $requiredDirs) {
        if (Test-Path $dir) {
            Write-Status "Directory: $dir" "OK"
        } else {
            $missingDirs += $dir
        }
    }
    
    if ($missingDirs.Count -gt 0) {
        Write-Status "Missing directories:" "WARN"
        foreach ($dir in $missingDirs) {
            Write-Status "  - $dir" "WARN"
        }
    }
    
    return $true
}

function Test-VercelConfiguration {
    Write-Status "Validating Vercel configuration..." "INFO"
    
    # Check vercel.json
    if (Test-Path "vercel.json") {
        try {
            $vercelConfig = Get-Content "vercel.json" -Raw | ConvertFrom-Json
            Write-Status "vercel.json found and readable" "OK"
            
            # Basic validation
            if ($vercelConfig.builds -and $vercelConfig.builds[0].src -eq "src/main.py") {
                Write-Status "Main application configured" "OK"
            } else {
                Write-Status "Main application not properly configured" "WARN"
            }
            
            if ($vercelConfig.builds[0].use -eq "@vercel/python") {
                Write-Status "Python runtime configured" "OK"
            } else {
                Write-Status "Python runtime not configured" "ERROR"
                return $false
            }
        }
        catch {
            Write-Status "Error reading vercel.json: $($_.Exception.Message)" "ERROR"
            return $false
        }
    } else {
        Write-Status "vercel.json not found" "ERROR"
        return $false
    }
    
    # Check main application file
    if (Test-Path "src/main.py") {
        Write-Status "Main application file found" "OK"
    } else {
        Write-Status "src/main.py not found" "ERROR"
        return $false
    }
    
    return $true
}

function Test-EnvironmentConfiguration {
    Write-Status "Checking environment configuration..." "INFO"
    
    if (Test-Path ".env.production.template") {
        Write-Status "Production environment template found" "OK"
    } else {
        Write-Status ".env.production.template not found" "ERROR"
        return $false
    }
    
    return $true
}

function Test-Dependencies {
    if ($SkipTests) {
        Write-Status "Skipping dependency test" "WARN"
        return $true
    }
    
    Write-Status "Testing dependencies..." "INFO"
    
    # Check if pyproject.toml exists
    if (-not (Test-Path "pyproject.toml")) {
        Write-Status "pyproject.toml not found" "ERROR"
        return $false
    }
    
    # Try poetry check
    try {
        Write-Status "Checking Poetry configuration..." "INFO"
        & poetry check 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Poetry configuration valid" "OK"
        } else {
            Write-Status "Poetry configuration has issues" "WARN"
        }
    }
    catch {
        Write-Status "Poetry check failed: $($_.Exception.Message)" "WARN"
    }
    
    return $true
}

# Main validation logic
Write-Host "======================================================" -ForegroundColor Blue
Write-Host "Autonomous Software Foundry - Deployment Validation" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

$allTestsPassed = $true

# Run validation checks
if (-not (Test-Prerequisites)) { $allTestsPassed = $false }
if (-not (Test-ProjectStructure)) { $allTestsPassed = $false }
if (-not (Test-Dependencies)) { $allTestsPassed = $false }
if (-not (Test-VercelConfiguration)) { $allTestsPassed = $false }
if (-not (Test-EnvironmentConfiguration)) { $allTestsPassed = $false }

# Show summary
Write-Host "`n======================================================" -ForegroundColor Blue
Write-Host "Validation Summary" -ForegroundColor Blue
Write-Host "======================================================" -ForegroundColor Blue

if ($allTestsPassed) {
    Write-Status "All validation checks passed!" "OK"
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Install Vercel CLI: npm install -g vercel" -ForegroundColor Yellow
    Write-Host "2. Login to Vercel: vercel login" -ForegroundColor Yellow
    Write-Host "3. Configure environment variables in Vercel dashboard" -ForegroundColor Yellow
    Write-Host "4. Deploy: vercel --prod" -ForegroundColor Yellow
    
    Write-Status "Validation completed successfully!" "OK"
    exit 0
} else {
    Write-Status "Some validation checks failed" "ERROR"
    Write-Host "Please fix the issues above before deploying" -ForegroundColor Yellow
    exit 1
}