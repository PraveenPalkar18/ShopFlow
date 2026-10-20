$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$top = (git -C $repo rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or [System.IO.Path]::GetFullPath($top) -ne [System.IO.Path]::GetFullPath($repo)) {
    throw "Refusing to reset: scripts must run from the ShopFlow repository."
}
git -C $repo switch baseline
if ($LASTEXITCODE -ne 0) { throw "Could not switch to baseline. This script will not discard uncommitted changes." }
