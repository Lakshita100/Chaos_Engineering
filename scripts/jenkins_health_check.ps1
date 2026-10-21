$ErrorActionPreference = 'Stop'
$ready = $false

for ($attempt = 1; $attempt -le 15; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri 'http://localhost:5000/health' -TimeoutSec 3
        if ($health.status -eq 'healthy') {
            Write-Host 'Flask app is healthy.'
            $ready = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $ready) {
    Write-Error 'Flask health check failed at http://localhost:5000/health.'
    exit 1
}
