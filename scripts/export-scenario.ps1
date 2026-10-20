param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^PR-(0[1-9]|1[0-2])$")]
    [string]$Scenario,
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$top = (git -C $repo rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or [System.IO.Path]::GetFullPath($top) -ne [System.IO.Path]::GetFullPath($repo)) {
    throw "Refusing to export: scripts must run from the ShopFlow repository."
}
$number = [int]$Scenario.Substring(3)
$names = @(
    "docs-typo", "pricing-rounding", "admin-auth", "dependency-update",
    "inventory-regression", "auth-regression", "discount-codes", "unsafe-config",
    "cancel-restock", "search-and-payment", "currency-propagation", "validation-refactor"
)
$branch = "pr-{0:D2}-{1}" -f $number, $names[$number - 1]
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repo ("evaluation\exports\" + $Scenario + ".patch")
}
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
if (-not $resolvedOutput.StartsWith($repo + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output must be inside the ShopFlow repository."
}
$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
git -C $repo show-ref --verify --quiet ("refs/heads/" + $branch)
if ($LASTEXITCODE -ne 0) { throw "Unknown scenario branch: $branch" }
git -C $repo diff --binary baseline $branch --output=$resolvedOutput
if ($LASTEXITCODE -ne 0) { throw "Git failed to export scenario diff." }
Write-Output $resolvedOutput
