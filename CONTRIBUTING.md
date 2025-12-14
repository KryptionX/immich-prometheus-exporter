# Contributing

## Setup
```bash
git clone https://github.com/KryptionX/immich-prometheus-exporter
cd immich-prometheus-exporter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Testing
```bash
python -m pytest
```

## Commit Guidelines
- Use conventional commits when possible (feat, fix, chore)
- Add tests for new metrics or API changes

## Release
- Tag with `vX.Y.Z`
- GitHub Actions will build and push images to GHCR
