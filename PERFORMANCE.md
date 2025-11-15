# Performance Profiling in Ticca

Ticca includes built-in performance profiling to help identify slow startup and runtime operations.

## Enabling Profiling

### Option 1: Use start.sh (Automatic)

Profiling is **automatically enabled** when using the `start.sh` launcher:

```bash
./start.sh  # Profiling enabled automatically
```

### Option 2: Manual Environment Variable

Set the `TICCA_PROFILE` environment variable before running:

```bash
export TICCA_PROFILE=1
ticca
```

Or run it inline:

```bash
TICCA_PROFILE=1 ticca
```

**What gets profiled:**
- High-level operation timing (e.g., "Import TUI", "Run TUI", "Load API keys")
- Detailed function-level analysis using Python's built-in `cProfile`
- Both reports are generated together

### Option 3: Direct Launch (No Profiling)

Running directly via `uv` or as a module will **NOT** enable profiling by default:

```bash
uv run ticca        # No profiling
python -m ticca     # No profiling
ticca               # No profiling
```

## What Gets Profiled

When profiling is enabled, Ticca will time:

- Argument parsing
- Configuration loading
- API key loading
- Model validation
- Agent initialization
- DBOS initialization
- TUI import and startup
- Startup callbacks
- And more...

## Viewing Results

### Console Output

When you exit Ticca (or it completes), you'll see a performance report printed to the console showing all operations that took more than 10ms, sorted by duration.

Example output:
```
================================================================================
TICCA PERFORMANCE REPORT
================================================================================
Total elapsed time: 2.45s

Showing operations taking >10ms:
--------------------------------------------------------------------------------
Run TUI................................................. 1.23s ( 50.2%)
Import TUI.............................................. 456ms ( 18.6%)
Load API keys to environment............................ 234ms (  9.6%)
Ensure config exists.................................... 123ms (  5.0%)
Startup callbacks....................................... 45ms (  1.8%)
Argument parsing........................................ 23ms (  0.9%)
================================================================================
```

### Detailed Function Profiling Output

When profiling is enabled, you'll also see a detailed breakdown of every function call using cProfile:

```
================================================================================
DETAILED PROFILING STATS (cProfile)
================================================================================
Top 50 slowest functions:

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      125    0.012    0.000    1.234    0.010 textual/app.py:342(compose)
       47    0.008    0.000    0.876    0.019 ticca/agents/base.py:89(__init__)
      312    0.006    0.000    0.543    0.002 pydantic/main.py:156(__init__)
      ...
================================================================================
```

**Understanding the columns:**
- `ncalls`: Number of times the function was called
- `tottime`: Total time spent in this function (excluding subfunctions)
- `cumtime`: Cumulative time (including subfunctions) - **this is usually most important**
- `percall`: Average time per call
- `filename:lineno(function)`: Where the function is defined

### Performance Report File

The performance data is automatically saved to:
```
~/.ticca/perf_report.txt
```

This file contains the complete performance breakdown and can be analyzed after each run.

## Adding Custom Profiling

You can add profiling to your own code:

```python
from ticca.perf import time_block

# Time a block of code
with time_block("My expensive operation"):
    # ... your code here
    pass

# Time nested operations
with time_block("Parent operation"):
    do_something()

    with time_block("Child operation", depth=1):
        do_something_else()
```

## Profiling Tips

1. **First run vs subsequent runs**: The first run will be slower as it downloads the embedding model and caches it to `~/.ticca/embedding_model/`

2. **Focus on the big wins**: Look for operations taking >100ms - these are usually the best optimization targets

3. **Check the detailed stats**: If "Run TUI" shows a long delay, check the cProfile output (automatically included) to see which Textual components or theme operations are slow

4. **Import timing**: Large imports (like TUI) can be slow. Consider lazy importing when possible.

5. **Embedding model**: The Qwen 0.6B embedding model now loads asynchronously in the background, so it shouldn't block startup anymore

6. **Interpreting cProfile output**: Focus on functions with high `cumtime` (cumulative time) - these include time spent in subfunctions and are usually the bottlenecks

7. **Performance overhead**: Profiling adds some overhead (~5-10% slower). This is normal and helps identify bottlenecks.

## Disabling Profiling

Simply unset the environment variable or don't set it:

```bash
unset TICCA_PROFILE
ticca
```

Or run without it:

```bash
ticca  # No profiling
```

## Performance Optimization History

### Recent Improvements

- **Asynchronous embedding model loading**: The Qwen 0.6B embedding model (used for semantic search in ChromaDB) now loads in a background thread, reducing startup time significantly
- **Model caching**: Embedding models are cached to `~/.ticca/embedding_model/` and reused across sessions
- **Lazy initialization**: ChromaDB and embedding models only load if semantic search is enabled
