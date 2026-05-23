param(
    [Parameter(Mandatory = $true)]
    [string]$Password,
    [string]$User = "postgres",
    [string]$Database = "cyberify_kb"
)

$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
$env:PGPASSWORD = $Password

Write-Host "Testing connection as $User..."
    & $psql -U $User -h 127.0.0.1 -d postgres -tAc "SELECT 1" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "PostgreSQL login failed. Check username/password."
    exit 1
}

$exists =     & $psql -U $User -h 127.0.0.1 -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$Database'"
    if ($exists -ne "1") {
    Write-Host "Creating database $Database..."
    & $psql -U $User -h 127.0.0.1 -d postgres -c "CREATE DATABASE $Database"
}

Write-Host "Enabling pgvector extension..."
& $psql -U $User -h 127.0.0.1 -d $Database -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "Done. Update .env DATABASE_URL to:"
Write-Host "postgres://${User}:YOUR_PASSWORD@127.0.0.1:5432/$Database"
