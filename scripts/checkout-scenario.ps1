param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^PR-(0[1-9]|1[0-2])$")]
    [string]$Scenario
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$top = (git -C $repo rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or [System.IO.Path]::GetFullPath($top) -ne [System.IO.Path]::GetFullPath($repo)) {
    throw "Refusing to switch branches: scripts must run from the ShopFlow repository."
}
$branch = "pr-" + $Scenario.Substring(3) + "-" + @(
    "docs-typo", "pricing-rounding", "admin-auth", "dependency-update",
    "inventory-regression", "auth-regression", "discount-codes", "unsafe-config",
    "cancel-restock", "search-and-payment", "currency-propagation", "validation-refactor"
)[([int]$Scenario.Substring(3) - 1)]
git -C $repo switch $branch
if ($LASTEXITCODE -ne 0) { throw "Could not check out $branch. Preserve or commit local changes before switching." }
