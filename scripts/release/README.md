# release

## Purpose
Release-note, changelog, and tag-version tooling for CI.

## Owns
- Tag parsing (`vX.Y.Z`, `vX.Y.Z-rc.N`).
- Conventional commit changelog generation.
- Release body rendering for GitHub Release.

## Entry Points
- `python -m scripts.release.release notes --tag v1.2.3 --out release_notes.md`
- `python -m scripts.release.release notes --tag v1.2.3-rc.1 --out release_notes.md --update-changelog CHANGELOG.md`
- `python -m scripts.release.release changelog --tag v1.2.3 --changelog CHANGELOG.md --out release_notes.md`
- `python -m scripts.release.release changelog --changelog CHANGELOG.md` (auto-read tag from `GITHUB_REF_NAME`)

## Not Here
- Package build and upload steps (handled in workflow files).
