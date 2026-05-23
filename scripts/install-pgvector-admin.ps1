# Run PowerShell as Administrator, then execute this script.
$pg = "C:\Program Files\PostgreSQL\17"
$src = "$env:TEMP\pgvector-pg17"
if (-not (Test-Path $src)) {
    $zip = "$env:TEMP\pgvector-pg17.zip"
    Invoke-WebRequest -Uri "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/0.8.2_17.6/vector.v0.8.2-pg17.zip" -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $src -Force
}
Copy-Item "$src\include\*" "$pg\include\" -Recurse -Force
Copy-Item "$src\lib\*" "$pg\lib\" -Force
Copy-Item "$src\share\*" "$pg\share\" -Recurse -Force
Restart-Service postgresql-x64-17
Write-Host "pgvector files copied. Enable with: CREATE EXTENSION vector;"
