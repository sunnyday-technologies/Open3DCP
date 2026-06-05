param(
  [string]$PublishDir
)

# Build a WEB-ONLY publish directory for open3dcp.org.
#
# Open3DCP serves from the repo ROOT (GitHub Pages, .nojekyll). This allowlist
# copies the public web content into a clean publish dir for Cloudflare Pages.
# Repo machinery (scripts/, tools/, .github/) and local-only in-development material
# kept outside this public repo are never referenced here, so they cannot reach the
# deploy. Fail-loud checks abort if a blocked dir, CAD file, oversized file, or
# secret-looking string lands in the publish dir.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir ".."))

if ([string]::IsNullOrWhiteSpace($PublishDir)) {
  $PublishDir = Join-Path $RepoRoot ".cloudflare\pages\open3dcp"
}
$Target = [System.IO.Path]::GetFullPath($PublishDir)
if (-not $Target.StartsWith($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to write outside project root: $Target"
}
if (Test-Path -LiteralPath $Target) { Remove-Item -LiteralPath $Target -Recurse -Force }
New-Item -ItemType Directory -Path $Target -Force | Out-Null

function Copy-PublicFile {
  param([string]$RelativePath)
  $Source = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Missing public file: $RelativePath" }
  $Dest = Join-Path $Target $RelativePath
  New-Item -ItemType Directory -Path (Split-Path -Parent $Dest) -Force | Out-Null
  Copy-Item -LiteralPath $Source -Destination $Dest -Force
}

function Copy-PublicDirectory {
  param([string]$RelativePath)
  $Source = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $Source -PathType Container)) { throw "Missing public directory: $RelativePath" }
  $Dest = Join-Path $Target $RelativePath
  New-Item -ItemType Directory -Path $Dest -Force | Out-Null
  Copy-Item -Path (Join-Path $Source "*") -Destination $Dest -Recurse -Force
}

# --- ALLOWLIST -------------------------------------------------------------
# CNAME and .nojekyll are GitHub-Pages-specific and intentionally omitted
# (Cloudflare sets the custom domain in the dashboard).
$rootFiles = @(
  "index.html", "favicon.svg",
  "robots.txt", "sitemap.xml", "llms.txt",
  "dc64666f8b365e677b9a887307e73b38.txt",          # IndexNow / site-verification key
  "Open3DCP_SCHEMA.md", "Open3DCP_TERM_JUSTIFICATION.md", "CHANGELOG.md",
  "CITATION.cff", "LICENSE", ".zenodo.json", "README.md", "AGENTS.md"
)
foreach ($f in $rootFiles) { Copy-PublicFile $f }

$publicDirs = @(
  "assets", "examples", "schema-reference", "intake",
  "submissions", "crosswalk", "sql", ".well-known"
)
foreach ($d in $publicDirs) { Copy-PublicDirectory $d }

# --- FAIL-LOUD TRIPWIRES ---------------------------------------------------
$publishFiles = Get-ChildItem -LiteralPath $Target -Recurse -File

# 1. No machinery / private / build dirs in the output.
$blocked = @("scripts", "tools", ".github", ".git", "drafts", "reference_docs",
             "intake-demo", "playbooks", "docs", "fonts", "publication", "node_modules")
foreach ($b in $blocked) {
  if (Test-Path -LiteralPath (Join-Path $Target $b)) { throw "Blocked path reached publish dir: $b" }
}

# 1b. The two private crosswalk CSVs must never ship (they live in Open3DCP-private).
foreach ($csv in @("dataset_comparison.csv", "printing_variables_to_relational.csv")) {
  if (Test-Path -LiteralPath (Join-Path $Target "crosswalk\$csv")) { throw "Private crosswalk CSV reached publish dir: $csv" }
}

# 2. No CAD, nothing over Cloudflare's 25 MiB cap.
$cadExt = @(".stl",".step",".stp",".3mf",".f3d",".f3z",".sldprt",".sldasm",".ipt",".iam",".iges",".igs",".x_t",".x_b",".dwg",".dxf")
$cad = $publishFiles | Where-Object { $cadExt -contains $_.Extension.ToLower() }
if ($cad) { throw "CAD file(s) reached the publish dir: $($cad.FullName -join ', ')" }
$big = $publishFiles | Where-Object { $_.Length -gt 25MB }
if ($big) { throw "File(s) over Cloudflare's 25 MiB limit: $(($big | ForEach-Object { $_.Name }) -join ', ')" }

# 3. No secret-looking strings (scan text files only).
$textExt = @(".html",".js",".mjs",".css",".json",".jsonl",".txt",".xml",".svg",".md",".cff",".yaml",".yml",".sql")
$secretPatterns = @(
  "AKIA[0-9A-Z]{16}",
  "-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----",
  "ghp_[A-Za-z0-9_]{20,}",
  "xox[baprs]-[A-Za-z0-9-]{20,}",
  "sk_live_[A-Za-z0-9]{20,}",
  "sk-[A-Za-z0-9]{32,}"
)
$hits = @()
foreach ($file in ($publishFiles | Where-Object { $textExt -contains $_.Extension.ToLower() })) {
  $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
  if ($null -eq $content) { continue }
  foreach ($p in $secretPatterns) { if ($content -match $p) { $hits += $file.FullName; break } }
}
if ($hits.Count -gt 0) { throw "Secret-like pattern(s) found in: $(($hits | Sort-Object -Unique) -join ', ')" }

# --- REPORT ----------------------------------------------------------------
$bytes = ($publishFiles | Measure-Object -Property Length -Sum).Sum
Write-Output "open3dcp publish dir ready: $Target"
Write-Output "Files: $($publishFiles.Count)"
Write-Output "Bytes: $bytes"
