# Creates the issue labels (from .github/labels.yml) and the starting roadmap issues
# in Knapis522/lightburn-grid-arranger. Safe to run again: labels are updated,
# issues whose title already exists (open or closed) are skipped.
#
# Requires GitHub CLI:  winget install GitHub.cli   then   gh auth login
# Run from the project folder:
#   powershell -ExecutionPolicy Bypass -File tools\github_setup.ps1

$ErrorActionPreference = "Stop"
$Repo = "Knapis522/lightburn-grid-arranger"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) not found. Install it: winget install GitHub.cli, then run: gh auth login"
}
gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "Not logged in. Run: gh auth login" }

# --- labels (keep in sync with .github/labels.yml) -------------------------------------
$labels = @(
    @("bug", "d73a4a", "Something does not work"),
    @("enhancement", "a2eeef", "New feature or change"),
    @("translation", "0e8a16", "User interface or help text in one of the 8 languages"),
    @("lightburn-format", "5319e7", "Reading or writing .lbrn2 projects, LightBurn compatibility (KAL tests)"),
    @("help wanted", "008672", "Extra attention is needed - e.g. a native-speaker translation review"),
    @("needs-sample", "fbca04", "A reduced sample project (without customer data) is needed to reproduce"),
    @("milestone", "1d76db", "Roadmap milestone (see docs/ROADMAP.md)")
)
foreach ($l in $labels) {
    gh label create $l[0] --repo $Repo --color $l[1] --description $l[2] --force | Out-Null
    Write-Host "label: $($l[0])"
}

# --- issues ------------------------------------------------------------------------------
$existing = @(gh issue list --repo $Repo --state all --limit 1000 --json title --jq ".[].title")
$tmp = Join-Path $env:TEMP "grid_arranger_issue_body.md"
$utf8 = New-Object System.Text.UTF8Encoding $false

function New-Issue([string]$Title, [string[]]$Labels, [string]$Body) {
    if ($script:existing -contains $Title) { Write-Host "skip (exists): $Title"; return }
    [System.IO.File]::WriteAllText($script:tmp, $Body, $script:utf8)
    $ghArgs = @("issue", "create", "--repo", $script:Repo, "--title", $Title, "--body-file", $script:tmp)
    foreach ($x in $Labels) { $ghArgs += @("--label", $x) }
    gh @ghArgs
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed: $Title" }
}

New-Issue "KAL-08: verify multi-board output in LightBurn" @("milestone", "lightburn-format") @"
Roadmap: **V20-01-PAGES** (spec v1.29-1.30). Implemented and covered by automatic tests; the saved projects still need to be opened in LightBurn.

- [ ] Several boards saved as LightBurn pages: page names, order, every board placed from the origin corner
- [ ] Boards saved as separate files (``...__board1.lbrn2``, ...)
- [ ] Arranging a project that already has pages keeps the other pages unchanged
- [ ] Shared geometry (original placed only on a later board) opens correctly
- [ ] Preview and Frame on each page

Steps: test page "Testy vice desek". Results go to ``docs/FORMAT_COMPATIBILITY.md``.
"@

New-Issue "Manual test of item quantities (V11-02)" @("milestone") @"
Roadmap: **V11-ACCEPT**. Quantities (pieces per item, spec v1.25) are implemented and covered by ``tests/integration/test_quantities.py``; a manual check in the app and in LightBurn is missing.

- [ ] Set different quantities for several items, save, count the pieces in LightBurn
- [ ] Quantities together with several boards and with filling the last board
- [ ] Undo / redo of quantity changes
"@

New-Issue "Release v0.1.0-alpha.6" @("milestone") @"
Pre-release with: omitting objects, LightBurn pages, several boards (sequential / even / by item, fill last board, pages or separate files), renaming items, Ctrl+A, unsaved-changes warning, remembering the last project folder.

Depends on: KAL-08 and the manual quantity test.

- [ ] Full test suite green on Windows
- [ ] ``docs/RELEASE_CHECKLIST.md``
- [ ] Release notes ``docs/releases/v0.1.0-alpha.6.md``
- [ ] Update from alpha.5 inside the app works
"@

New-Issue "MVP-ACCEPT: acceptance of MVP-01...08" @("milestone") @"
Roadmap: **MVP-ACCEPT**. Go through the MVP criteria of the specification and the test plan (``docs/TEST_PLAN.md``) and record the results.

- [ ] MVP-01 ... MVP-08 checked
- [ ] Manual test T-MVP-26
- [ ] Final test of saved projects in LightBurn on a real job
- [ ] HELP-01: help (F1) opens in the built EXE on Windows
"@

New-Issue "T-I18N-21: check cut-off texts in all languages on Windows" @("milestone", "translation") @"
Switch the language in **Settings -> General -> Language** and go through the main window, the Settings window, messages and the help (F1). Look for cut-off or overlapping texts.

- [ ] cs
- [ ] en
- [ ] de
- [ ] sk
- [ ] pl
- [ ] fr
- [ ] es
- [ ] it
"@

$langs = @(
    @("German", "de"), @("Slovak", "sk"), @("Polish", "pl"),
    @("French", "fr"), @("Spanish", "es"), @("Italian", "it")
)
foreach ($lg in $langs) {
    $name = $lg[0]; $code = $lg[1]
    New-Issue "Native-speaker review: $name ($code)" @("translation", "help wanted") @"
The $name translation was machine-made and has not been reviewed by a native speaker yet. Until it is, the language is not "fully supported" (gate L10N-PUBLIC-01).

**What to review**
- User interface: ``translations/gridarranger_$code.ts`` (Qt Linguist or a text editor)
- Help (F1): ``src/grid_arranger/gui/help/$code/*.md`` (8 pages)

Please keep the laser terms consistent with the glossary in ``docs/TRANSLATING.md`` and keep placeholders such as ``{name}`` and ``%n`` unchanged.

Small fixes: comment here or use the *Translation fix* issue form. Larger fixes: a pull request (see ``docs/TRANSLATING.md``). Contributions are accepted under the project's MIT licence.
"@
}

Remove-Item $tmp -ErrorAction SilentlyContinue
Write-Host "Done."
