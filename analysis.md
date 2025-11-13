# TUI Performance Analysis - Ticca

## Executive Summary

The Ticca TUI, particularly the settings dialog, exhibits slow rendering performance. This analysis identifies the root causes and provides actionable recommendations for optimization.

**Primary Issues:**
1. Settings dialog renders all tabs simultaneously with heavy I/O operations on mount
2. Right sidebar performs unnecessary full refreshes every second
3. Chat view uses expensive Rich text conversions and complex message combining logic
4. Inefficient DOM queries and frequent layout recalculations throughout

---

## 1. Settings Dialog Performance Issues

### Location: `ticca/tui/screens/settings.py`

### Critical Problems:

#### 1.1 Heavy `on_mount()` Operations (lines 690-759)

**Issue:** The settings dialog performs extensive work when opened:

```python
def on_mount(self) -> None:
    # Calls 25+ config getters
    get_yolo_mode()
    get_allow_recursion()
    get_global_model_name()
    get_vqa_model_name()
    # ... 20+ more config reads

    # Heavy loading operations
    self.load_theme_options()      # Loads ALL themes from disk
    self.load_model_options()      # Loads model config, iterates all models
    self.load_agent_pinning_table() # Creates dynamic widgets for ALL agents
    self.load_api_keys()           # Reads .env file from disk
```

**Impact:**
- File I/O: Reads `.env`, `puppy.cfg`, model config, theme config
- ~30+ function calls before dialog appears
- Blocks UI thread during mount

#### 1.2 Renders All 6 Tabs Simultaneously (lines 320-688)

**Issue:** All tab content is created upfront in `compose()`:

```python
def compose(self) -> ComposeResult:
    with TabbedContent(id="settings-tabs"):
        with TabPane("General", id="general"):        # Tab 1 - ~30 widgets
        with TabPane("Models & AI", id="models"):     # Tab 2 - ~20 widgets
        with TabPane("History & Context", id="history"): # Tab 3 - ~30 widgets
        with TabPane("Appearance", id="appearance"):  # Tab 4 - ~40 widgets
        with TabPane("Agents & Integrations", id="integrations"): # Tab 5 - ~30 widgets
        with TabPane("API Keys & Status", id="status"): # Tab 6 - ~40 widgets
```

**Impact:**
- Creates ~190 widgets at once
- User only sees one tab, but all are rendered
- Massive widget tree increases layout calculation time

#### 1.3 Dynamic Widget Creation in `load_agent_pinning_table()` (lines 831-867)

**Issue:** Creates Select widgets dynamically for every agent:

```python
def load_agent_pinning_table(self):
    agents = get_available_agents()
    models_data = ModelFactory.load_config()  # Loads from disk

    # Creates model options list
    model_options = [("(default)", "")]
    for model_name, model_config in models_data.items():
        model_options.append(...)  # Builds list for EVERY model

    # Creates a row for EACH agent
    for agent_name, display_name in agents.items():
        agent_row = Container(classes="agent-pin-row")
        container.mount(agent_row)  # Mount operation
        agent_row.mount(Label(...))
        agent_row.mount(Select(...))  # Creates Select with full model list
```

**Impact:**
- Loads model config from disk
- Creates nested containers and Select widgets at runtime
- Multiple mount operations slow down rendering

#### 1.4 File I/O in `load_api_keys()` (lines 869-912)

**Issue:** Reads and parses `.env` file synchronously:

```python
def load_api_keys(self):
    env_file = Path.cwd() / ".env"
    env_values = {}
    if env_file.exists():
        with open(env_file, "r") as f:  # Synchronous file read
            for line in f:
                # Parse each line
```

**Impact:**
- Synchronous disk I/O blocks rendering
- Happens every time settings dialog opens

#### 1.5 Excessive CSS Complexity

**Issue:** 311 lines of CSS with many specific selectors:

```css
/* Multiple selectors for each widget type */
.setting-row { ... }
.setting-label { ... }
.setting-input { ... }
.switch-row { ... }
.agent-pin-row { ... }
/* etc. */
```

**Impact:**
- CSS parsing and application takes time
- Many selector matches during layout

---

## 2. Chat View Performance Issues

### Location: `ticca/tui/components/chat_view.py`

### Critical Problems:

#### 2.1 Expensive Rich Object Conversions (lines 282-316, 406-436)

**Issue:** Converts Rich objects to strings using console rendering:

```python
from io import StringIO
from rich.console import Console

# Convert Rich content to string
if hasattr(last_message.content, "__rich_console__"):
    string_io = StringIO()
    temp_console = Console(file=string_io, width=80, ...)
    temp_console.print(last_message.content)
    existing_content = string_io.getvalue().rstrip("\n")
```

**Impact:**
- Creates temporary Console and StringIO objects
- Renders Rich content to string just to concatenate
- Happens on every message combination
- Performance scales poorly with message count

#### 2.2 Complex Message Combining Logic (lines 354-463)

**Issue:** Multiple nested conditionals for message grouping:

```python
def add_message(self, message: ChatMessage) -> None:
    # Check suppression
    if self._should_suppress_message(message):  # Config read
        return

    # Enhanced grouping check
    if message.group_id is not None and message.group_id in self.group_widgets:
        self._append_to_existing_group(message)  # Complex logic
        return

    # Old grouping logic (fallback)
    if message.group_id is not None and self.messages and ...:
        self._append_to_existing_group(message)
        return

    # Category-based combining
    if self.messages and self._last_message_category == message_category and ...:
        # More complex logic
```

**Impact:**
- Multiple condition checks per message
- State tracking across multiple variables
- Harder to optimize and reason about

#### 2.3 SafeMarkdownViewer for Agent Responses (lines 549-589)

**Issue:** Creates full MarkdownViewer widgets:

```python
if message.type == MessageType.AGENT_RESPONSE:
    message_widget = SafeMarkdownViewer(
        content,
        show_table_of_contents=False,
        classes=css_class
    )
```

**Impact:**
- MarkdownViewer is a heavy widget with full document parsing
- Creates document tree for markdown rendering
- Much heavier than simple Static widget

#### 2.4 Frequent Layout Recalculations (lines 447, 453, 461)

**Issue:** Forces layout refresh frequently:

```python
self._last_widget.refresh(layout=True)  # Forces layout recalculation
self.refresh(layout=True)               # Entire view layout recalc
```

**Impact:**
- Layout recalculation is expensive
- Called on every message combination
- Cascades through widget tree

#### 2.5 Config Reads on Every Message (lines 193-213)

**Issue:** Reads config for message suppression:

```python
def _should_suppress_message(self, message: ChatMessage) -> bool:
    from ticca.config import (
        get_suppress_informational_messages,  # Config read
        get_suppress_thinking_messages,       # Config read
    )
    suppress_thinking = get_suppress_thinking_messages()
    suppress_info = get_suppress_informational_messages()
```

**Impact:**
- Config reads on every message
- Imports happen on every call (though Python caches modules)

---

## 3. Right Sidebar Performance Issues

### Location: `ticca/tui/components/right_sidebar.py`

### Critical Problems:

#### 3.1 Unnecessary 1-Second Auto-Refresh (lines 102-106)

**Issue:** Updates display every second unconditionally:

```python
def on_mount(self) -> None:
    self._update_display()
    # Auto-refresh every second for live updates
    self.set_interval(1.0, self._update_display)
```

**Impact:**
- Updates even when nothing changed
- Wastes CPU cycles
- 60 unnecessary updates per minute

#### 3.2 Full Display Rewrite on Every Update (lines 143-239)

**Issue:** Clears and rewrites entire RichLog:

```python
def _update_display(self) -> None:
    status_text = Text()

    # Build entire display from scratch
    status_text.append("Active Agent:\n", ...)
    status_text.append("LLM Model:\n", ...)
    # ... build entire text

    # Clear and rewrite
    status_display.clear()
    status_display.write(status_text)
```

**Impact:**
- Recreates entire Text object
- Clears and rewrites display
- No differential updates

#### 3.3 Agent Discovery on Every Update (lines 166-211)

**Issue:** Queries all agents on each refresh:

```python
def _update_display(self) -> None:
    try:
        from ticca.agents import get_available_agents
        from ticca.agents.agent_manager import get_current_agent, _AGENT_HISTORIES
        agents = get_available_agents()  # Discovers all agents
        current_agent = get_current_agent()  # Gets current agent

        for agent_id, agent_display in agents.items():
            # Query message count for each agent
```

**Impact:**
- Unnecessary agent discovery
- Accesses agent histories
- Happens every second

#### 3.4 Multiple Reactive Watchers (lines 108-131)

**Issue:** Each reactive variable triggers full display update:

```python
def watch_context_used(self) -> None:
    self._update_display()

def watch_context_total(self) -> None:
    self._update_display()

def watch_message_count(self) -> None:
    self._update_display()

# 6 watchers total, each calls _update_display()
```

**Impact:**
- Multiple updates for related changes
- Should batch updates

---

## 4. Main App Performance Issues

### Location: `ticca/tui/app.py`

### Critical Problems:

#### 4.1 Theme Registration on Startup (lines 255-281)

**Issue:** Registers ALL themes at mount:

```python
def _register_themes(self) -> None:
    ThemeManager.initialize()
    themes = ThemeManager.list_themes()

    # Register each theme
    for theme_name in themes.keys():
        theme_obj = ThemeManager.get_theme(theme_name)  # Loads theme
        if theme_obj:
            textual_theme = create_textual_theme(theme_obj)
            self.register_theme(textual_theme)
```

**Impact:**
- Loads all theme definitions
- Creates Textual theme objects for all
- Only one theme is used at a time

#### 4.2 Heavy `on_mount()` Operations (lines 295-384)

**Issue:** Multiple heavy operations on mount:

```python
def on_mount(self) -> None:
    self._register_themes()              # Loads all themes
    register_callback(...)               # Callback registration
    get_current_agent()                  # Agent loading

    self.call_after_refresh(self.start_message_renderer_sync)
    self.call_after_refresh(self.preload_agent_on_startup)  # Heavy!
    self.call_after_refresh(self.maybe_prompt_restore_autosave)
    self.call_after_refresh(self.focus_input_field)

    self._update_right_sidebar()         # Full sidebar update
```

**Impact:**
- Sequential operations delay initial render
- Agent preloading is particularly heavy
- Multiple file reads

#### 4.3 Frequent DOM Queries with `query_one()` (throughout)

**Issue:** `query_one()` used extensively:

```python
# Examples from app.py
status_bar = self.query_one(StatusBar)          # Line 228, 329, 918, etc.
chat_view = self.query_one("#chat-view", ChatView)  # Line 423, 451, 478, etc.
input_field = self.query_one("#input-field", CustomTextArea)  # Line 563, 619, etc.
sidebar = self.query_one(Sidebar)              # Line 824, 1189, etc.
```

**Impact:**
- DOM traversal on every query
- No caching of widget references
- Called hundreds of times during session

#### 4.4 Periodic Context Updates During Agent Execution (lines 1124-1166)

**Issue:** Updates every 0.5 seconds while agent is busy:

```python
async def _periodic_context_update(self) -> None:
    while self.agent_busy:
        self._update_right_sidebar()  # Full update
        await asyncio.sleep(0.5)      # Every 500ms
```

**Impact:**
- High frequency updates
- Full sidebar recalculation each time
- Compounds with 1-second interval in sidebar

---

## 5. Additional Performance Concerns

### 5.1 File Tree Panel

**Location:** `ticca/tui/components/file_tree.py`

**Issue:** DirectoryTree can be slow with large directories
- Lines 76: Creates DirectoryTree for entire working directory
- No lazy loading or filtering

### 5.2 Message History Processing

**Location:** `ticca/tui/app.py` (lines 1086-1122)

**Issue:** Recalculates token counts on every update:

```python
def _update_right_sidebar(self) -> None:
    message_history = agent.get_message_history()
    total_tokens = sum(
        agent.estimate_tokens_for_message(msg) for msg in message_history
    )  # Recalculates on every update
```

**Impact:**
- O(n) operation where n = message count
- No caching of token counts
- Called frequently during agent execution

---

## Recommendations

### Priority 1: Settings Dialog (Highest Impact)

1. **Lazy Tab Loading**
   - Only render active tab content
   - Create widgets on tab switch
   - **Expected improvement:** 5-10x faster initial load

2. **Cache Config Values**
   - Load all config once on mount
   - Store in instance variables
   - **Expected improvement:** Eliminate 25+ function calls

3. **Defer Heavy Operations**
   - Load model options only when Models tab is accessed
   - Load agent pinning only when Integrations tab is accessed
   - **Expected improvement:** 3-5x faster dialog open

4. **Async File I/O**
   - Use `asyncio.to_thread()` for file reads
   - Show loading indicator
   - **Expected improvement:** Non-blocking, better UX

5. **Simplify CSS**
   - Reduce selector specificity
   - Use fewer classes
   - **Expected improvement:** Faster CSS application

### Priority 2: Right Sidebar

1. **Smart Updates**
   - Only update when values actually change
   - Use reactive variable comparison
   - **Expected improvement:** 90% reduction in unnecessary updates

2. **Increase Update Interval**
   - Change from 1s to 5s or remove entirely
   - Update only on state changes
   - **Expected improvement:** 80% reduction in update overhead

3. **Differential Updates**
   - Update only changed parts of display
   - Don't clear and rewrite entire RichLog
   - **Expected improvement:** Faster updates

4. **Cache Agent Discovery**
   - Cache available agents list
   - Only refresh when needed
   - **Expected improvement:** Eliminate repeated discovery

### Priority 3: Chat View

1. **Avoid Rich Conversions**
   - Keep content as strings when possible
   - Only use Rich for final display
   - **Expected improvement:** 2-3x faster message combining

2. **Simplify Message Combining**
   - Reduce conditional complexity
   - Single code path for combining
   - **Expected improvement:** Better maintainability, slight performance gain

3. **Use Static Instead of MarkdownViewer**
   - MarkdownViewer is heavy
   - Use Static with Markdown Rich object
   - **Expected improvement:** Lighter widgets

4. **Batch Layout Updates**
   - Avoid `refresh(layout=True)` in loops
   - Batch updates when adding multiple messages
   - **Expected improvement:** Fewer layout recalculations

5. **Cache Suppression Config**
   - Read suppression config once
   - Store as instance variables
   - **Expected improvement:** Eliminate config reads per message

### Priority 4: Main App

1. **Lazy Theme Loading**
   - Only load and register current theme
   - Load others on demand
   - **Expected improvement:** Faster startup

2. **Cache Widget References**
   - Store widget references on mount
   - Avoid repeated `query_one()` calls
   - **Expected improvement:** Faster widget access

3. **Reduce Update Frequency**
   - Change periodic updates from 0.5s to 2s
   - Only update when agent state changes
   - **Expected improvement:** Lower CPU usage

4. **Cache Token Counts**
   - Calculate incrementally as messages are added
   - Store running total
   - **Expected improvement:** O(1) instead of O(n)

---

## Performance Testing Recommendations

1. **Add Profiling**
   - Use `cProfile` or `py-spy` to profile settings dialog opening
   - Measure time in `on_mount()`, `compose()`, and loading functions

2. **Benchmark Key Operations**
   - Time settings dialog open/close
   - Time message addition with/without Rich conversions
   - Measure sidebar update overhead

3. **Monitor Resource Usage**
   - Track CPU usage during normal operation
   - Monitor memory usage over time
   - Check for memory leaks in long sessions

4. **Add Performance Metrics**
   - Log timing for slow operations (>100ms)
   - Track layout recalculation frequency
   - Monitor DOM query counts

---

## Estimated Impact Summary

| Optimization | Difficulty | Expected Improvement | Priority |
|-------------|-----------|---------------------|----------|
| Lazy tab loading in settings | Medium | 5-10x faster dialog | **Critical** |
| Cache config in settings | Easy | Remove ~30 function calls | **Critical** |
| Smart sidebar updates | Easy | 90% fewer updates | **High** |
| Remove 1s auto-refresh | Easy | Lower CPU usage | **High** |
| Cache widget references | Easy | Faster widget access | **Medium** |
| Avoid Rich conversions | Medium | 2-3x faster messages | **Medium** |
| Lazy theme loading | Easy | Faster startup | **Low** |

---

## Conclusion

The primary performance bottleneck is the settings dialog, which:
1. Renders all 6 tabs simultaneously (~190 widgets)
2. Performs extensive file I/O on mount
3. Calls 25+ config getters synchronously
4. Creates dynamic widgets for all agents and models

Secondary issues include:
- Right sidebar's unnecessary 1-second auto-refresh
- Chat view's expensive Rich object conversions
- Frequent layout recalculations throughout
- No caching of widget references or config values

Implementing the Priority 1 recommendations alone would likely provide a 5-10x improvement in settings dialog rendering speed. Combined with Priority 2 and 3 optimizations, the overall TUI experience would be significantly more responsive.
