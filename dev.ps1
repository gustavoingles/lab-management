# dev.ps1 — Start the LabManager development server
# Usage:
#   .\dev.ps1           — run locally with uv (requires PostgreSQL running)
#   .\dev.ps1 -Docker   — run via Docker Compose (requires Docker Desktop)
#   .\dev.ps1 -Seed     — force re-seed demo data, then exit
param(
    [switch]$Docker,
    [switch]$Seed
)

$ErrorActionPreference = "Stop"

# ── Docker path ─────────────────────────────────────────────────────────────
if ($Docker) {
    $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerCmd) {
        Write-Error "Docker not found. Install Docker Desktop and try again."
        exit 1
    }
    Write-Host "Starting with Docker Compose..." -ForegroundColor Cyan
    Write-Host "  http://localhost:8000/  (claudia@lab.test / labtest)" -ForegroundColor Green
    docker compose up --build
    exit $LASTEXITCODE
}

# ── Local path (uv) ──────────────────────────────────────────────────────────
$uv = "C:\Users\gusta\AppData\Local\Programs\Anki\uv.exe"
if (-not (Test-Path $uv)) {
    Write-Error "uv not found at: $uv`nInstall uv or update the `$uv variable in dev.ps1."
    exit 1
}

# Ensure .env exists with local defaults
if (-not (Test-Path ".env")) {
    Write-Host ".env not found — creating with local defaults..." -ForegroundColor Yellow
    @"
SECRET_KEY=django-insecure-labmanager-dev-key-change-in-production
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@localhost:5432/lab_management
"@ | Out-File -Encoding utf8 ".env"
}

# Sync dependencies
Write-Host "Syncing dependencies..." -ForegroundColor Cyan
& $uv sync --quiet
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Apply migrations
Write-Host "Applying migrations..." -ForegroundColor Cyan
& $uv run python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Error "migrate failed — is PostgreSQL running and DATABASE_URL correct in .env?"
    exit 1
}

# Seed demo data
Write-Host "Seeding demo data..." -ForegroundColor Cyan
& $uv run python manage.py seed_db
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Seed) {
    Write-Host "Done." -ForegroundColor Green
    exit 0
}

# Start dev server
Write-Host ""
Write-Host "  Server running at http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "  claudia@lab.test / labtest  (gestor)" -ForegroundColor DarkGray
Write-Host "  renato@lab.test  / labtest  (almoxarife)" -ForegroundColor DarkGray
Write-Host "  marina@lab.test  / labtest  (solicitante)" -ForegroundColor DarkGray
Write-Host "  iuri@lab.test    / labtest  (manutencao)" -ForegroundColor DarkGray
Write-Host ""
& $uv run python manage.py runserver
