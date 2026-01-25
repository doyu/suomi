# AnkiWeb Sync Setup Guide

## Overview

This guide explains how to set up automatic AnkiWeb sync for headless servers using Docker + Xvfb + Anki + AnkiConnect.

**Status**: 🚧 Design complete, implementation pending

## Quick Start (Future)

```bash
# 1. Build Docker image
docker build -f Dockerfile.ankiweb -t suomi-ankiweb .

# 2. Run with AnkiWeb credentials
docker run -d \
  -e ANKIWEB_USERNAME=your_username \
  -e ANKIWEB_PASSWORD=your_password \
  -p 8765:8765 \
  suomi-ankiweb

# 3. Use in Python
from suomi.ankiweb import addnotes_with_sync

addnotes_with_sync("MyDeck", "vocabulary.tsv")
# Cards are added and automatically synced to AnkiWeb
```

## Architecture

```
Docker Container
├── Xvfb (virtual display :99)
├── Anki Desktop (headless)
│   └── AnkiConnect plugin (:8765)
└── Python + suomi package
    ├── suomi.anki (existing)
    └── suomi.ankiweb (new)
```

## Components

### 1. Notebook: `nbs/04_ankiweb.ipynb`

Provides AnkiWeb sync functionality:

- **`configure_ankiweb()`** - Set credentials from env vars
- **`sync_to_ankiweb()`** - Sync with retry logic
- **`addnotes_with_sync()`** - Add cards + auto sync

### 2. Docker: `Dockerfile.ankiweb`

Docker image with:
- Ubuntu 22.04
- Xvfb for virtual display
- Anki Desktop
- AnkiConnect plugin
- Python environment

### 3. Entrypoint: `docker-entrypoint.sh`

Startup script that:
1. Starts Xvfb on display :99
2. Launches Anki in headless mode
3. Waits for AnkiConnect to be ready
4. Executes user command

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANKIWEB_USERNAME` | AnkiWeb username | Yes |
| `ANKIWEB_PASSWORD` | AnkiWeb password | Yes |
| `DISPLAY` | X11 display (default: :99) | No |

**Security Note**: Never commit credentials to git. Use Docker secrets or `.env` files.

## API Usage

### Basic Usage

```python
from suomi.ankiweb import addnotes_with_sync

# Add cards and sync automatically
addnotes_with_sync("Finnish::Vocabulary", "tsvs/01_greetings.tsv")
```

### Without Auto-Sync

```python
from suomi.anki import addnotes
from suomi.ankiweb import sync_to_ankiweb

# Add cards without sync
addnotes("Finnish::Vocabulary", "tsvs/01_greetings.tsv")

# Manually sync later
sync_to_ankiweb()
```

### Error Handling

```python
from suomi.ankiweb import addnotes_with_sync, SyncError

try:
    addnotes_with_sync("MyDeck", "vocab.tsv")
except SyncError as e:
    print(f"Sync failed: {e}")
    print("Cards were added but not synced to AnkiWeb")
    # Retry sync manually later
```

## Implementation TODO

- [ ] Complete Dockerfile (install Anki + AnkiConnect)
- [ ] Complete docker-entrypoint.sh (Xvfb + Anki startup)
- [ ] Implement `configure_ankiweb()` credential storage
- [ ] Test AnkiConnect `sync` action with credentials
- [ ] Add tests for sync functionality
- [ ] Document first-time AnkiWeb authentication flow
- [ ] Multi-user support (multiple Anki profiles)

## References

- [AnkiConnect API Documentation](https://foosoft.net/projects/anki-connect/)
- [Anki Manual - Command Line](https://docs.ankiweb.net/misc.html)
- Design Document: `docs/plans/2026-01-25-ankiweb-sync-design.md`

## Troubleshooting

### AnkiConnect Not Responding

```bash
# Check if Anki is running
docker exec <container> ps aux | grep anki

# Check AnkiConnect port
docker exec <container> curl http://localhost:8765
```

### Sync Failures

- Verify AnkiWeb credentials are correct
- Check network connectivity
- Review Anki logs in container

### Xvfb Issues

```bash
# Verify Xvfb is running
docker exec <container> ps aux | grep Xvfb

# Check display
docker exec <container> echo $DISPLAY
```
