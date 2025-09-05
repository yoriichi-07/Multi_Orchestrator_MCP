# Autonomous Software Foundry - Fly.io Deployment Scripts
# PowerShell scripts for Windows-friendly deployment and management

# deploy.ps1 - Main deployment script

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$WaitForHealth = $true
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue

function Write-ColorOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-FlyCliInstalled {
    try {
        $flyVersion = flyctl version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Fly CLI is installed: $flyVersion" $Green
            return $true
        }
    }
    catch {
        Write-ColorOutput "❌ Fly CLI is not installed or not in PATH" $Red
        Write-ColorOutput "📥 Please install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/" $Yellow
        return $false
    }
}

function Test-FlyAuthenticated {
    try {
        $authStatus = flyctl auth whoami 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Fly CLI is authenticated: $authStatus" $Green
            return $true
        }
    }
    catch {
        Write-ColorOutput "❌ Fly CLI is not authenticated" $Red
        Write-ColorOutput "🔐 Please run: flyctl auth login" $Yellow
        return $false
    }
}

function Initialize-FlyApp {
    param([string]$AppName)
    
    Write-ColorOutput "🚀 Initializing Fly.io application: $AppName" $Blue
    
    # Check if app already exists
    try {
        $appStatus = flyctl status --app $AppName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ App $AppName already exists" $Green
            return $true
        }
    }
    catch {
        # App doesn't exist, create it
        Write-ColorOutput "📱 Creating new Fly.io app: $AppName" $Yellow
        
        if ($Force) {
            flyctl apps create $AppName --generate-name=$false
        } else {
            $confirm = Read-Host "Create new app '$AppName'? (y/N)"
            if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                flyctl apps create $AppName --generate-name=$false
            } else {
                Write-ColorOutput "❌ App creation cancelled" $Red
                return $false
            }
        }
    }
    
    return $LASTEXITCODE -eq 0
}

function Deploy-Application {
    param([string]$AppName, [string]$ConfigFile)
    
    Write-ColorOutput "🚀 Deploying to $AppName using $ConfigFile" $Blue
    
    # Check if config file exists
    if (-not (Test-Path $ConfigFile)) {
        Write-ColorOutput "❌ Config file not found: $ConfigFile" $Red
        return $false
    }
    
    # Deploy the application
    Write-ColorOutput "📦 Starting deployment..." $Yellow
    
    try {
        if ($Environment -eq "staging") {
            flyctl deploy --app $AppName --config $ConfigFile --strategy "immediate"
        } else {
            flyctl deploy --app $AppName --config $ConfigFile --strategy "rolling"
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Deployment successful!" $Green
            return $true
        } else {
            Write-ColorOutput "❌ Deployment failed with exit code: $LASTEXITCODE" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ Deployment error: $($_.Exception.Message)" $Red
        return $false
    }
}

function Wait-ForHealthCheck {
    param([string]$AppName)
    
    if (-not $WaitForHealth) {
        return $true
    }
    
    Write-ColorOutput "🔍 Waiting for health check..." $Yellow
    
    $maxAttempts = 30
    $attemptCount = 0
    $healthUrl = "https://$AppName.fly.dev/health"
    
    while ($attemptCount -lt $maxAttempts) {
        try {
            $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 10
            if ($response.status -eq "healthy") {
                Write-ColorOutput "✅ Health check passed!" $Green
                Write-ColorOutput "🌐 Application URL: $healthUrl" $Blue
                return $true
            }
        }
        catch {
            # Health check failed, continue waiting
        }
        
        $attemptCount++
        Write-ColorOutput "⏳ Attempt $attemptCount/$maxAttempts - waiting 10 seconds..." $Yellow
        Start-Sleep -Seconds 10
    }
    
    Write-ColorOutput "❌ Health check timeout after $maxAttempts attempts" $Red
    return $false
}

function Show-DeploymentSummary {
    param([string]$AppName, [string]$Environment)
    
    Write-ColorOutput "`n🎉 Deployment Summary" $Blue
    Write-ColorOutput "======================" $Blue
    Write-ColorOutput "App Name: $AppName" $Green
    Write-ColorOutput "Environment: $Environment" $Green
    Write-ColorOutput "Health URL: https://$AppName.fly.dev/health" $Green
    Write-ColorOutput "MCP Capabilities: https://$AppName.fly.dev/mcp/capabilities" $Green
    Write-ColorOutput "Dashboard: https://$AppName.fly.dev/dashboard" $Green
    
    Write-ColorOutput "`n📊 Useful Commands:" $Blue
    Write-ColorOutput "flyctl status --app $AppName" $Yellow
    Write-ColorOutput "flyctl logs --app $AppName" $Yellow
    Write-ColorOutput "flyctl ssh console --app $AppName" $Yellow
    Write-ColorOutput "flyctl metrics --app $AppName" $Yellow
}

# Main deployment logic
Write-ColorOutput "🚀 Autonomous Software Foundry - Fly.io Deployment" $Blue
Write-ColorOutput "Environment: $Environment" $Yellow

# Determine app name and config file based on environment
if ($Environment -eq "staging") {
    $appName = "asf-staging"
    $configFile = "fly.staging.toml"
    
    # Create staging config if it doesn't exist
    if (-not (Test-Path $configFile)) {
        Copy-Item "fly.toml" $configFile
        (Get-Content $configFile) -replace 'app = "autonomous-software-foundry"', 'app = "asf-staging"' | Set-Content $configFile
        Write-ColorOutput "📝 Created staging config: $configFile" $Yellow
    }
} else {
    $appName = "autonomous-software-foundry"
    $configFile = "fly.toml"
}

# Pre-flight checks
Write-ColorOutput "`n🔍 Running pre-flight checks..." $Blue

if (-not (Test-FlyCliInstalled)) { exit 1 }
if (-not (Test-FlyAuthenticated)) { exit 1 }

# Validate project structure
$requiredFiles = @("pyproject.toml", "Procfile", "runtime.txt", $configFile)
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-ColorOutput "❌ Missing required files:" $Red
    foreach ($file in $missingFiles) {
        Write-ColorOutput "  - $file" $Red
    }
    exit 1
}

Write-ColorOutput "✅ All required files present" $Green

# Initialize app if needed
if (-not (Initialize-FlyApp $appName)) {
    exit 1
}

# Deploy application
if (-not (Deploy-Application $appName $configFile)) {
    exit 1
}

# Wait for health check
if (-not (Wait-ForHealthCheck $appName)) {
    Write-ColorOutput "⚠️ Deployment completed but health check failed" $Yellow
    Write-ColorOutput "Check logs: flyctl logs --app $appName" $Yellow
} else {
    # Show deployment summary
    Show-DeploymentSummary $appName $Environment
}

Write-ColorOutput "`n🎯 Deployment process completed!" $Green