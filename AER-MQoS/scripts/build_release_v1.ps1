# Build AER-MQoS-v1.0.zip for public GitHub release (Windows).
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$StagingParent = Join-Path (Split-Path $Root -Parent) "AER-MQoS-release-staging"
$Dest = Join-Path $StagingParent "AER-MQoS"
$ZipPath = Join-Path (Split-Path $Root -Parent) "AER-MQoS_v1.0.zip"

if (Test-Path $StagingParent) { Remove-Item $StagingParent -Recurse -Force }
New-Item -ItemType Directory -Path $Dest -Force | Out-Null

$ExcludeDirs = @(
    "anomalies", "_archive", "archive", "explications",
    "Section-tex\.pydeps", "Section-tex\.venv",
    "Section-tex\sim\multi_seed_hybrid_archive",
    "Section-tex\sim\multi_seed_measured_pilot8",
    "simulations\real\logs",
    "code_source_AER_MQoS\build",
    "__pycache__", ".git"
)
$ExcludeFiles = @(
    "*.aux", "*.log", "*.out", "*.blg", "*.bbl", "*.synctex.gz",
    "*.fdb_latexmk", "*.fls", "*.pyc", "*.docx", ".DS_Store",
    "main-ieee-tables.pdf", "main-ieee-tables.aux", "main-ieee-tables.log", "main-ieee-tables.out",
    "Fig_1_Architecture_AER_MQoS.png", "Fig_2_DODAG_Path_Levels.png", "texput.log"
)
$ExcludeNames = @(
    "anomalies.md", "checklist.md",
    "prochaine-proposition.md",
    "article_AER-MQoS_ieeetran_stub.tex",
    "DEV_ONLY_generate_hybrid_multi_seed.py",
    "build_release_v1.ps1", "build_github_release.sh"
)

function Should-Skip($relPath, $name, $isDir) {
    foreach ($d in $ExcludeDirs) {
        if ($relPath -like "*$d*") { return $true }
    }
    if ($relPath -match '(^|[\\/])build([\\/]|$)') { return $true }
    foreach ($n in $ExcludeNames) {
        if ($name -eq $n) { return $true }
    }
    if (-not $isDir) {
        foreach ($pat in $ExcludeFiles) {
            if ($name -like $pat) { return $true }
        }
    }
    return $false
}

$copyRoots = @("Section-tex", "simulations", "code_source_AER_MQoS")
foreach ($cr in $copyRoots) {
    $srcDir = Join-Path $Root $cr
    if (-not (Test-Path $srcDir)) { continue }
    Get-ChildItem $srcDir -Recurse -Force | ForEach-Object {
        $rel = $_.FullName.Substring($srcDir.Length).TrimStart("\")
        $targetRel = Join-Path $cr $rel
        if (Should-Skip $targetRel $_.Name $_.PSIsContainer) { return }
        $tgt = Join-Path $Dest $targetRel
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $tgt -Force | Out-Null
        } else {
            $parent = Split-Path $tgt -Parent
            if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            Copy-Item $_.FullName $tgt -Force
        }
    }
}

Copy-Item (Join-Path $Root "Section-tex\main-ieee.pdf") (Join-Path $Dest "main-ieee.pdf") -Force

# Public documentation (written at release time)
@'
MIT License

Copyright (c) 2026 Madani Belacel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'@ | Set-Content (Join-Path $Dest "LICENSE") -Encoding UTF8

@'
# AER-MQoS

Replication package for the manuscript *AER-MQoS: A Context-Aware Multi-Objective RPL Extension for QoS-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power IoT Networks*.

## Overview

IPv6 RPL is the de facto routing core for many constrained IoT deployments, yet a single rank semantics rarely fits mixed traffic: urgent control flows, bulk telemetry, and long-lived maintenance packets impose different latency and energy pressures. **AER-MQoS** (Adaptive Energy-aware Multi-Objective QoS Routing) unifies class-aware rank shaping, residual-energy and link-reliability proxies, and UDP-edge weighted round-robin scheduling in one Contiki-NG firmware line built on stock `rpl-lite`. The evaluated builds use experimental Objective Code Point 8 and keep trust/energy/QoS terms as **local decision variables**—no project-specific DIO/DAO TLVs on the wire.

Release **v1.0** (May 2026) provides the IEEE camera-ready PDF, complete LaTeX sources, reference firmware, Cooja scenarios, parsing scripts, and the **four-seed** measured campaign (`N = 4`, 1800 s per cell) behind Figures 3–11 and the evaluation tables.

## Author

**Madani Belacel**  
Abdelhamid Ibn Badis University of Mostaganem, Mostaganem, Algeria  
E-mail: madani.belacel@univ-mosta.dz  
ORCID: [0009-0003-2928-9565](https://orcid.org/0009-0003-2928-9565)

## How to cite this package

```bibtex
@misc{belacel2026aermqos,
  author       = {Belacel, Madani},
  title        = {{AER-MQoS}: A Context-Aware Multi-Objective {RPL} Extension for {QoS}-Aware, Energy-Aware, and Link-Reliability-Informed Routing in Low-Power {IoT} Networks --- Replication Package v1.0},
  year         = {2026},
  howpublished = {Software and manuscript sources},
  note         = {Abdelhamid Ibn Badis University of Mostaganem, Algeria}
}
```

Prior work on RPLMQoS and RPL-AER appears in `Section-tex/bib/references.bib`.

## Repository layout

| Path | Contents |
|------|----------|
| `main-ieee.pdf` | Camera-ready IEEE two-column manuscript (v1.0) |
| `Section-tex/` | LaTeX sources (`main-ieee.tex`, sections, preamble, `bib/references.bib`) |
| `Section-tex/Figures/` | Figure PDFs (Figs. 1–11) |
| `Section-tex/scripts/` | Figure generation and log parsing (`generate_figures_matplotlib.py`, `parse_cooja_logs.py`, …) |
| `Section-tex/sim/multi_seed/` | Measured Cooja CSVs (four seeds, four firmware tags) |
| `Section-tex/sim/DATA_PROVENANCE.md` | Data lineage for figures and tables |
| `code_source_AER_MQoS/` | Contiki-NG modules (`rpl-of-aer-plus.c`, `aer_rpl_plus.c`, `aer_qos_queue.c`, …) |
| `simulations/` | Cooja `.csc` scenarios and `run_multi_seed_campaign.sh` |
| `INSTALL.md` | Toolchain setup, PDF build, figure and campaign reproduction |
| `LICENSE` | MIT license for this repository snapshot |

## Compile the paper

From `Section-tex/`:

```bash
pdflatex -interaction=nonstopmode main-ieee.tex
bibtex main-ieee
pdflatex -interaction=nonstopmode main-ieee.tex
pdflatex -interaction=nonstopmode main-ieee.tex
```

The root `main-ieee.pdf` is a copy of the output above. See **INSTALL.md** for dependencies and troubleshooting.

## Regenerate figures and replay Cooja

- **Figures 3–11:** `python3 scripts/generate_figures_matplotlib.py --from-csv sim/multi_seed` (run inside `Section-tex/`).
- **Full campaigns:** `simulations/real/run_multi_seed_campaign.sh` (JDK 21, Contiki-NG; expect long runtimes).

Committed CSVs under `Section-tex/sim/multi_seed/` match the statistics reported in `main-ieee.pdf`. Record your toolchain versions in `Section-tex/BUILD_NOTES.txt` when refreshing data.

## License

This snapshot is released under the **MIT License** (`LICENSE`). Firmware builds on **Contiki-NG** (BSD-style license). The bundled **IEEEtran** class files follow their own distribution terms.
'@ | Set-Content (Join-Path $Dest "README.md") -Encoding UTF8

@'
# Installation and reproduction (AER-MQoS v1.0)

Consolidated release (**June 2026**): measured evaluation uses **four independent Cooja seeds** at **1800 s** per cell (four firmware tags, lossless and lossy UDGM). Committed CSVs are under `Section-tex/sim/multi_seed/`.

## 1. Prerequisites

### Manuscript (LaTeX)
- TeX Live 2022 or newer: `pdflatex`, `bibtex`
- Recommended: `texlive-latex-extra` (`microtype`, `ragged2e`, …)

### Figures
- Python 3.10+
- `pip install matplotlib pillow`

### Cooja / Contiki-NG
- **JDK 21** (required by recent Cooja Gradle builds)
- Contiki-NG checkout compatible with `code_source_AER_MQoS/`
- Cooja as provided with your Contiki-NG tree

Record your toolchain in `Section-tex/BUILD_NOTES.txt` after refreshing data (Contiki `git describe`, `gcc --version`, campaign date).

## 2. Build the IEEE PDF

From the repository root:

```bash
cd Section-tex
pdflatex -interaction=nonstopmode main-ieee.tex
bibtex main-ieee
pdflatex -interaction=nonstopmode main-ieee.tex
pdflatex -interaction=nonstopmode main-ieee.tex
```

Output: `Section-tex/main-ieee.pdf` (a copy is also provided at the repository root as `main-ieee.pdf`).

On Linux/macOS you may use `Section-tex/scripts/build_pdfs.sh` to build both the author draft (`main.pdf`) and the IEEE version.

## 3. Regenerate measurement figures (Figs. 3–11)

```bash
cd Section-tex
export MPLBACKEND=Agg   # headless systems
python3 scripts/generate_figures_matplotlib.py --from-csv sim/multi_seed
```

Figures are written to `Section-tex/Figures/`. The manifest is `Section-tex/figures_manifest.csv`. Protocol CSV tags are mapped to plot labels via `scripts/protocol_aliases.py`.

## 4. Reproduce Cooja multi-seed campaigns

1. Build firmware variants from `code_source_AER_MQoS/` (see `code_source_AER_MQoS/README.md` and `simulations/README_CAMPAIGNS.md`).
2. Configure `CONTIKI` / Cooja paths in your environment.
3. Run from `simulations/real/`:

```bash
cd simulations/real
./run_multi_seed_campaign.sh
```

Default manuscript bundle: **four seeds** (`20260601`–`20260604`), **1800 s** simulation time, lossless and lossy UDGM channels, four firmware tags. Parsed CSVs land under `Section-tex/sim/multi_seed/` when using the project parsing scripts (`parse_cooja_logs.py`, `analyze_multi_seed_stats.py` in `simulations/real/` or `Section-tex/scripts/` as documented in the campaign README).

**Note:** Full campaigns are compute-intensive (tens of hours on a typical workstation). The committed `sim/multi_seed/` directory contains the measured CSVs used for v1.0 of the paper.

## 5. Data provenance

See `Section-tex/sim/DATA_PROVENANCE.md` and `Section-tex/Figures/FIGURES_DATA_TRACEABILITY.md`.

## 6. Troubleshooting

| Issue | Hint |
|-------|------|
| Undefined citations | Run the full `pdflatex` → `bibtex` → `pdflatex` ×2 chain |
| Matplotlib display error | Set `MPLBACKEND=Agg` |
| Cooja / Gradle fails | Verify JDK 21 (`java -version`) |
| Missing CSV for a figure | Regenerate campaign or check `figures_manifest.csv` |
'@ | Set-Content (Join-Path $Dest "INSTALL.md") -Encoding UTF8

@'
# LaTeX build artifacts
*.aux
*.log
*.out
*.blg
*.bbl
*.synctex.gz
*.fdb_latexmk
*.fls
*.toc
*.lof
*.lot

# Python
__pycache__/
*.py[cod]
.pydeps/
.venv/
venv/

# OS / editor
.DS_Store
Thumbs.db
*.swp
*~

# Cooja / simulation outputs (regenerate locally)
simulations/real/logs/
COOJA.testlog
*.testlog

# Contiki build artifacts
code_source_AER_MQoS/build/
**/build/sky/
**/build/cooja/

# Large optional archives
Section-tex/sim/multi_seed_hybrid_archive/

# Local build staging
AER-MQoS-release-staging/
'@ | Set-Content (Join-Path $Dest ".gitignore") -Encoding UTF8

# Sanitize public DATA_PROVENANCE (no internal-only tooling paths)
$dp = Join-Path $Dest "Section-tex\sim\DATA_PROVENANCE.md"
if (Test-Path $dp) {
    @'
# Data provenance for Section-tex figures

## Manuscript bundle (v1.0)

- **Figures 1–2:** conceptual schematics (`Fig_1_*`, `Fig_2_*`); no Cooja CSV input.
- **Figures 3–11:** generated by `Section-tex/scripts/generate_figures_matplotlib.py` from `Section-tex/sim/multi_seed/`. Status: `MEASURED` in `figures_manifest.csv`.
- **Campaign:** four independent Cooja seeds (`20260601`–`20260604`), lossless and lossy UDGM (`success_ratio=0.85`), four firmware tags, `SIM_TIMEOUT_MS=1800000`.
- **Logs:** produced under `simulations/real/` when re-running `run_multi_seed_campaign.sh`; committed CSVs are under `Section-tex/sim/multi_seed/`.

Record Contiki-NG `git describe` and `gcc --version` in `Section-tex/BUILD_NOTES.txt` when refreshing data.

## Parser notes

- `energy.csv`: `duty_cycle_pct` may mirror the NRE proxy until Energest is wired in.
- `ctrl.csv` / `stab.csv`: export-rate and adaptation proxies from METRIC lines when ICMP console counts are absent (see manuscript §VII).

## Figure manifest

See `Section-tex/figures_manifest.csv`.
'@ | Set-Content $dp -Encoding UTF8
}

if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
Compress-Archive -Path $Dest -DestinationPath $ZipPath -CompressionLevel Optimal

Write-Host "Created: $ZipPath"
Write-Host "Size MB:" ([math]::Round((Get-Item $ZipPath).Length / 1MB, 2))

# Scan for unwanted markers in text files
$bad = @('cursor','chatgpt','grok','deepseek','claude','gemini','openai')
$hits = @()
Get-ChildItem $Dest -Recurse -File -Include *.md,*.tex,*.txt,*.py,*.sh,*.c,*.h | ForEach-Object {
    $c = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if (-not $c) { return }
    foreach ($b in $bad) {
        if ($c -match $b) { $hits += "$($_.FullName): $b" }
    }
}
if ($hits.Count -gt 0) {
    Write-Warning "Review these paths before publishing:"
    $hits | Select-Object -First 20
} else {
    Write-Host "Scan OK: no AI-tool markers in text sources."
}

Remove-Item $StagingParent -Recurse -Force
Write-Host "Staging folder removed."
