$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$top = (git -C $repo rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or [System.IO.Path]::GetFullPath($top) -ne [System.IO.Path]::GetFullPath($repo)) {
    throw "Refusing to list branches: scripts must run from the ShopFlow repository."
}
git -C $repo branch --list "pr-*"
if ($LASTEXITCODE -ne 0) { throw "Git could not list scenario branches." }
