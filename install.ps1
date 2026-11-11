param(
    [string]$Target = (Join-Path $env:USERPROFILE ".claude\skills")
)

$ErrorActionPreference = "Stop"
$source = Join-Path $PSScriptRoot "skills\latex-review-materials"

if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    Write-Error "找不到 skills\latex-review-materials\SKILL.md，请在仓库根目录运行。"
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
$dest = Join-Path $Target "latex-review-materials"

if (Test-Path $dest) {
    $backup = "$dest.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Move-Item $dest $backup
    Write-Host "已备份旧版本到 $backup"
}

Copy-Item $source $dest -Recurse
Write-Host "已安装到 $dest"
Write-Host "重启会话后即可使用。"
