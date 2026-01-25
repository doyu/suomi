# AnkiWeb Sync Design

**Date**: 2026-01-25
**Status**: Design approved, implementation pending

## Overview

Enable headless server to sync cards to AnkiWeb automatically after adding them via AnkiConnect, without requiring Anki GUI.

## Requirements

- **R1**: Run on headless server (no GUI)
- **R2**: Add cards via AnkiConnect (existing `addnotes()`)
- **R3**: Auto-sync to AnkiWeb after card addition
- **R4**: One-way sync (Server → AnkiWeb only)
- **R5**: Retry on sync failure (3 attempts with exponential backoff)
- **R6**: Raise exception if sync fails after retries
- **R7**: Single user initially, multi-user support later
- **R8**: Credentials via environment variables

## Architecture

### System Components

```
┌─────────────────────────────────────────┐
│ Headless Server (Docker Container)     │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Xvfb (Virtual Display)            │  │
│  │   ↓                               │  │
│  │ Anki Desktop (Headless)           │  │
│  │   ↓                               │  │
│  │ AnkiConnect (HTTP :8765)          │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ suomi package                     │  │
│  │                                   │  │
│  │ • 03_anki.ipynb (existing)        │  │
│  │   - addnotes()                    │  │
│  │   - call()                        │  │
│  │                                   │  │
│  │ • 04_ankiweb.ipynb (new)          │  │
│  │   - sync_to_ankiweb()             │  │
│  │   - addnotes_with_sync()          │  │
│  │   - configure_ankiweb()           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
                   ↓
                AnkiWeb
```

### Layer Separation

1. **Infrastructure Layer**: Docker + Xvfb + Anki
2. **API Layer**: AnkiConnect
3. **Business Logic Layer**: `03_anki.ipynb` (card management)
4. **Sync Layer**: `04_ankiweb.ipynb` (AnkiWeb sync) ← NEW

## Implementation Plan

### Phase 1: Notebook Structure (Current)

Create `04_ankiweb.ipynb` with placeholder functions:

- `configure_ankiweb()` - Set AnkiWeb credentials
- `sync_to_ankiweb()` - Sync with retry logic
- `addnotes_with_sync()` - Wrapper around existing `addnotes()`

### Phase 2: Docker Setup (Next)

Create `Dockerfile` with:
- Ubuntu base
- Xvfb virtual display
- Anki desktop installation
- AnkiConnect plugin
- Python environment

### Phase 3: Integration & Testing

- Test sync functionality
- Error handling validation
- Integration with existing workflow

## API Design

### `configure_ankiweb(username=None, password=None)`

Configure AnkiWeb credentials for sync.

**Parameters**:
- `username`: AnkiWeb username (defaults to `ANKIWEB_USERNAME` env var)
- `password`: AnkiWeb password (defaults to `ANKIWEB_PASSWORD` env var)

**Raises**:
- `ValueError`: If credentials not provided

### `sync_to_ankiweb(max_retries=3)`

Sync local collection to AnkiWeb with retry logic.

**Parameters**:
- `max_retries`: Maximum retry attempts (default: 3)

**Raises**:
- `SyncError`: If sync fails after all retries

**Behavior**:
- Exponential backoff: 1s, 2s, 4s between retries

### `addnotes_with_sync(deck, tsv)`

Add notes from TSV and sync to AnkiWeb automatically.

**Parameters**:
- `deck`: Anki deck name
- `tsv`: Path to TSV file

**Raises**:
- `SyncError`: If sync fails after card addition
- Other exceptions from `addnotes()`

**Note**: Cards are added successfully even if sync fails. User can manually retry sync.

## Backward Compatibility

- Existing `addnotes()` in `03_anki.ipynb` remains unchanged
- Users can choose between:
  - `addnotes()` - No sync
  - `addnotes_with_sync()` - Auto sync

## Security

- Credentials stored in environment variables
- Never commit credentials to git
- Docker secrets or `.env` file for configuration

## Future Enhancements

- Multi-user support (multiple Anki profiles)
- Sync scheduling (cron-based)
- Sync status monitoring
- Selective sync (specific decks only)

## Open Questions

- Does AnkiConnect's `sync` action require pre-configured credentials in Anki?
- How to handle first-time AnkiWeb authentication in headless mode?
- Performance impact of Xvfb overhead?

## References

- AnkiConnect API: https://foosoft.net/projects/anki-connect/
- Anki sync protocol: (unofficial, needs investigation)
