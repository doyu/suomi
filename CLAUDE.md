# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Finnish language learning tool that generates MP3 audio files from text using the Piper TTS engine and syncs flashcard data to Anki via AnkiConnect. The project uses nbdev for literate programming, where all code is authored in Jupyter notebooks under `nbs/` and automatically exported to the `suomi/` package.

## Essential Commands

### Development Setup
```bash
pip install -e .                # Install in editable mode
```

### nbdev Workflow
```bash
nbdev_prepare                   # Export code, run tests, build docs (run before commits)
nbdev_test                      # Run notebook tests only
nbdev_export                    # Export notebook code to suomi/ package
nbdev_clean                     # Clean notebook metadata
```

### Testing
```bash
nbdev_test                      # Run all notebook tests
pytest suomi                    # Run standalone tests (if any)
```

## Code Architecture

### nbdev Literate Programming Workflow

This project follows nbdev's literate programming paradigm:

1. **Source of Truth**: All code is written in Jupyter notebooks under `nbs/`
2. **Code Generation**: `nbdev_prepare` or `nbdev_export` generates Python modules in `suomi/` from notebooks
3. **Never Edit Generated Files**: Do NOT manually edit files in `suomi/` - they will be overwritten. Always edit the corresponding notebooks.

### Key Notebooks

- **00_core.ipynb**: Core utilities (exports to `suomi.core`)
  - `find_files_recursive()`: Search directories recursively for files by extension and prefix
  - `ffr()`: Short alias for `find_files_recursive`
  - `cattxt()`: Read text files into list of lines
- **01_tsv.ipynb**: TSV utilities (currently minimal/empty)
- **02_mp3.ipynb**: Text-to-speech pipeline using Piper (exports to `suomi.mp3`)
  - `str2wav()`: Convert Finnish text to WAV using Piper TTS
  - `wav2mp3()`: Convert WAV to MP3 using ffmpeg
  - `str2mp3()`: Combined text-to-MP3 conversion
  - `mp3s()`: Batch process TSV files to generate audio files
  - `set_mp3_img_in()`: Update TSV files with mp3_path and img_path columns

- **03_sync.ipynb**: AnkiConnect integration (exports to `suomi.ankiconnect`)
  - `call()`: Generic AnkiConnect API wrapper
  - `addnotes()`: Bulk upload TSV data to Anki deck
  - Creates "Finnish-EN-JA-Audio-Image" note type with 3 card templates
  - Handles media file uploads (MP3 audio, PNG images)

### nbdev Special Comments

Notebooks use special directives:
- `#| default_exp module_name` - Sets the module name for exports
- `#| export` - Marks cells to export to the package
- `#| hide` - Hides cells from documentation
- `#| test` - Marks cells as tests for `nbdev_test`

### Data Flow

1. TSV files in `tsvs/` contain Finnish vocabulary with columns: `Finnish`, `English`, `Japanese`, `mp3_path`, `img_path`
2. `02_mp3.ipynb` processes TSVs to generate MP3 files in `audio/` directory
3. `03_sync.ipynb` uploads TSV data + media files to Anki via AnkiConnect API
4. Images are stored in `images/`, models in `models/` (Piper ONNX model: `fi_FI-harri-low.onnx`)

## External Dependencies

- **Piper TTS**: Command-line tool for Finnish text-to-speech (must be installed separately)
- **ffmpeg**: For audio conversion (WAV to MP3)
- **AnkiConnect**: Anki plugin that must be running (listens on http://localhost:8765)
- **httpx**: Python HTTP client for AnkiConnect API calls

## Important Notes from AGENTS.md

- **Answer in Japanese**: Respond to the user primarily in Japanese
- **Show code concisely**: Display proposed code changes concisely before modifying files
- **Module organization**: Keep modules small and focused; create new notebooks rather than growing existing ones
- **Testing**: Add tests for error cases (invalid TSV rows, missing audio files)
- **Assets**: Large binaries in `models/` should be git-ignored unless they are canonical fixtures
- **Notebook workflow**: Keep notebook outputs stripped unless they convey required context

## Development Workflow

1. Edit notebooks in `nbs/` directory
2. Mark cells for export with `#| export`
3. Run `nbdev_prepare` to export code, run tests, and build docs
4. Generated Python code appears in `suomi/` directory
5. Documentation is generated in `_docs/` directory

## Settings

Configuration is in `settings.ini`:
- Package name: `suomi`
- Min Python: 3.9
- Library path: `suomi/`
- Notebooks path: `nbs/`
- Docs path: `_docs/`

---

## Code Reviews

### 02_mp3.ipynb Review (Updated After Re-read)

#### Overview

After re-reading from disk, the notebook shows significant improvements. The previous critical issues have been addressed. This is an updated review of the current state.

#### Major Improvements Since Last Review

##### 1. Tests Fixed ✅
- Tests now use correct `fill_media_in(tsv, dirs=[...])` signature
- Custom directory test creates actual files and verifies paths correctly
- Empty TSV test works as expected

##### 2. `dump_tsv` Fixed ✅
```python
def dump_tsv(tsv: str):
    """Read and print TSV file contents."""
    with open(tsv, encoding="utf-8") as f:
        rows = []
        for i, row in enumerate(csv.DictReader(f, delimiter="\t")):
            rows.append(row)
        if rows:
            print(tsv, i, rows[i])
        else:
            print(tsv, "empty")
        return rows
```
- Now handles empty TSVs without crashing

##### 3. Better Documentation ✅
- Functions have proper type hints with comments
- `mp3s` has guards against missing "Finnish" field
- Docstrings are clear and comprehensive

#### All Critical Issues Resolved ✅

##### ✅ Issue #1: Temporary WAV File Cleanup (P1) - RESOLVED

**Status**: Fixed in current implementation

**Solution**: `text2mp3` now uses `try/finally` block to ensure temporary WAV files are cleaned up:

```python
def text2mp3(...):
    """Convert text to MP3 via WAV using Piper TTS and ffmpeg."""
    wav = "output.wav"
    try:
        text2wav(s, wav=wav, model=model)
        wav2mp3(wav=wav, mp3=mp3)
    finally:
        # Clean up temporary WAV file
        if os.path.exists(wav):
            os.remove(wav)
```

**Tests**: Includes test to verify cleanup even on conversion errors

##### ✅ Issue #2: Subprocess Error Handling (P0) - RESOLVED

**Status**: Fixed in current implementation

**Solution**: Both `text2wav` and `wav2mp3` now have comprehensive error handling:

```python
def text2wav(...):
    """Convert text to WAV using Piper TTS."""
    try:
        run(shlex.split(f"piper --model {model} --output_file {wav}"),
            input=s.encode(), check=True)
    except FileNotFoundError:
        raise RuntimeError(
            "Piper TTS not found. Install: pip install piper-tts\n"
            "Or download from: https://github.com/rhasspy/piper"
        )
    except CalledProcessError as e:
        raise RuntimeError(
            f"Piper TTS failed with exit code {e.returncode}\n"
            f"Check that model file exists: {model}\n"
            f"Error: {e}"
        )

def wav2mp3(...):
    """Convert WAV to MP3 using ffmpeg."""
    try:
        run(shlex.split(f"ffmpeg -hide_banner -loglevel error -y -i {wav} -codec:a libmp3lame -q:a 4 {mp3}"),
            check=True)
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Install:\n"
            "  Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Windows: Download from https://ffmpeg.org/"
        )
    except CalledProcessError as e:
        raise RuntimeError(
            f"ffmpeg conversion failed with exit code {e.returncode}\n"
            f"Input: {wav}, Output: {mp3}"
        )
```

**Tests**: Includes tests for missing binaries and conversion failures

#### Design Concerns

##### Concern #1: API Inconsistency Between Functions

```python
# fill_media_in: searches existing files
fill_media_in(tsv, dirs=["audio", "images"])

# mp3s: generates new files
mp3s(tsv, output_dir="audio", model='...')
```

**Observation**:
- `fill_media_in` uses `dirs` (plural, list) - for searching
- `mp3s` uses `output_dir` (singular, string) - for generation
- Both conceptually work with directories but use different terminology

**Is this a problem?**
- Semantically correct: `dirs` for search (multiple), `output_dir` for generation (single)
- But could be confusing if user expects consistency

**Recommendation**: Document this clearly or consider:
```python
# Option 1: Keep as is but add clear docstring
mp3s(tsv, output_dir="audio")  # Generates MP3s TO this directory
fill_media_in(tsv, dirs=["audio", "images"])  # Searches IN these directories

# Option 2: Unify terminology
mp3s(tsv, output_dir="audio")
fill_media_in(tsv, search_dirs=["audio", "images"])  # More explicit
```

**Decision**: Keep as is - semantics are correct, just needs good docs ✅

##### ✅ Concern #2: `ffr` Function Naming (P2) - RESOLVED

**Status**: Fixed in `00_core.ipynb`

**Solution**: Both `find_files_recursive` and `ffr` are now exported:

```python
#| export
def find_files_recursive(dirs, exts, prefix=""):
    """Recursively search directories for files with specified extensions and prefix.

    Searches each directory recursively and returns all files matching the given
    extensions and prefix. This is the full function name; use `ffr` for a shorter alias.
    """
    return _find_files_recursive(dirs, exts, prefix)

#| export
def ffr(dirs, exts, prefix=""):
    """Short alias for find_files_recursive.

    Convenient shorthand for find_files_recursive(). See that function for full documentation.
    """
    return find_files_recursive(dirs, exts, prefix)
```

**Benefits**:
- ✅ Self-documenting API with `find_files_recursive`
- ✅ Convenient shorthand with `ffr` for experienced users
- ✅ Follows Python conventions (like `pd` for pandas)
- ✅ Maintains backward compatibility

**Tests**: Includes test to verify both functions return identical results

##### Concern #3: glob Import Unused

**Location**: Cell `0a3ff5f6-b861-4dd3-aa1a-fa92b0ba5b37`

```python
import glob
```

**Observation**:
- Only used in `#| eval: false` cells (which now use `ffr` instead)
- Not used in any exported code
- Should be moved to `#| eval: false` cell or removed

**Impact**: Low - doesn't break anything, just unnecessary

#### Architecture Strengths

##### 1. Excellent Separation of Concerns

```
fill_media_in(tsv, dirs)
  ↓
  ├─ ffr() - Find all matching files
  ├─ _read_tsv_entries() - Parse TSV
  ├─ _assign_files_by_row() - Match files to rows (MP3)
  ├─ _assign_files_by_row() - Match files to rows (images)
  └─ Write updated TSV
```

Each helper has single responsibility ✅

##### 2. Smart File Matching Logic

- **Row-specific priority**: `{stem}_00.mp3` > common file
- **Extension priority**: `.png` > `.jpg`
- **Fallback rules**: Clear and documented
- **Empty row handling**: Skips truly empty rows ✅

##### 3. Type Safety

All functions have:
- Type hints on parameters
- Return type annotations
- Inline comments explaining types

Example:
```python
def _assign_files_by_row(
    all_files: list[str],  # All files found matching stem prefix
    stem: str,             # File stem (TSV filename without extension)
    extensions: list[str], # List of extensions to process
    num_rows: int,         # Number of rows in TSV
    use_common: bool = False # Whether to use common files
) -> list[str]:            # List of file paths, one per row
```

This is excellent! ✅

#### Summary

##### Current State: **Excellent** 🎉

| Aspect | Rating | Notes |
|--------|--------|-------|
| Architecture | ⭐⭐⭐⭐⭐ | Excellent separation of concerns |
| Type Safety | ⭐⭐⭐⭐⭐ | Comprehensive type hints |
| Documentation | ⭐⭐⭐⭐ | Good docstrings, could add more examples |
| Error Handling | ⭐⭐⭐⭐⭐ | Comprehensive error handling with helpful messages |
| Resource Management | ⭐⭐⭐⭐⭐ | Proper cleanup with try/finally blocks |
| Tests | ⭐⭐⭐⭐⭐ | Excellent coverage including error cases |

##### Completed Fixes (2026-01-25)

| Priority | Issue | Status |
|----------|-------|--------|
| ✅ P0 | Subprocess error handling | RESOLVED - Comprehensive try/except blocks |
| ✅ P1 | WAV file cleanup | RESOLVED - try/finally cleanup |
| ✅ P2 | Export `find_files_recursive` | RESOLVED - Both functions exported |
| 🟢 P3 | Remove unused `glob` import | Optional - Low priority |

##### Remaining Improvements (Optional)

**Nice to have** (non-critical):
- Clean up unused `glob` import in 02_mp3.ipynb (P3)

**Long-term** (future enhancements):
- Add `strict` mode to `fill_media_in` that validates all files exist
- Add logging for debugging
- Consider progress bars for `mp3s` with many files

##### Overall Assessment

**Status**: ✅ Production-ready and shipped

**Strengths**:
- ✅ Clean, modular architecture
- ✅ Excellent type safety
- ✅ Smart file matching logic
- ✅ Comprehensive error handling
- ✅ Proper resource management
- ✅ Tests cover both success and error cases
- ✅ Self-documenting API with convenient aliases

**No critical issues remaining** - All P0, P1, and P2 issues have been resolved.

**Recommendation**: Code is production-ready. Optional improvements can be addressed as needed.
