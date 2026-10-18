# Security

## What the application does on your computer

- It **only reads** the `.lbrn2` project you open and **writes a new file** you choose. It never overwrites the original or any existing file.
- It does not control the laser and does not talk to LightBurn.
- Its only network connection is the optional update check: an anonymous request to the public GitHub API (`api.github.com/repos/Knapis522/lightburn-grid-arranger/releases`). No project data, file names or personal data are sent. Automatic checking can be switched off in *Settings → Updates*.
- An update is installed only after you confirm it, and only if the downloaded installer matches the SHA-256 checksum published with the release (`SHA256SUMS.txt`).
- The installer and the application are not digitally signed yet; Windows SmartScreen may warn about them. Download only from this repository's Releases page.

## Reporting a problem

Please report security problems privately via GitHub: **Security → Report a vulnerability** in this repository (private vulnerability reporting). Do not attach customer projects; if a project is needed to reproduce the problem, reduce it to a minimal example first.

## Supported versions

Only the newest release receives fixes. The project is in an early pre-release (alpha) phase.
