$ErrorActionPreference = 'Stop'
$pgData = "$PWD/pgdata"
if (-not (Test-Path $pgData)) {
    New-Item -ItemType Directory -Force -Path $pgData | Out-Null
}

$env:PGDATA = $pgData
$env:PGHOST = 'localhost'
$env:PGPORT = '5432'
$env:PGUSER = 'postgres'
$env:PGPASSWORD = 'postgres'

if (-not (Get-Command initdb -ErrorAction SilentlyContinue)) {
    throw 'initdb not found. Please install PostgreSQL locally first.'
}

if (-not (Test-Path "$pgData/PG_VERSION")) {
    initdb -D $pgData -U postgres -W <<'EOF'
postgres
EOF
}

pg_ctl -D $pgData -l "$pgData/logfile" start

Write-Host 'Postgres started.'
