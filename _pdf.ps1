$repo = 'C:\Master In Ai\35 Builds and Experiments\M4U3 Computer Vision Repo'
Set-Location $repo
Write-Output '--- byte check ---'
Write-Output ('README.md = ' + (Get-Item -LiteralPath (Join-Path $repo 'README.md')).Length)
Write-Output ('build_reports.py = ' + (Get-Item -LiteralPath (Join-Path $repo 'tools\build_reports.py')).Length)
Write-Output '--- build ---'
& python tools\build_reports.py 2>&1
Write-Output '--- reports ---'
Get-ChildItem (Join-Path $repo 'reports') -File | Select-Object Name,Length,LastWriteTime | Out-String -Width 120
