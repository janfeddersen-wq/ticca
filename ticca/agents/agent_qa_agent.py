"""Quality Assurance Agent - Browser automation and testing agent."""

from .base_agent import BaseAgent


class QAAgent(BaseAgent):
    """Quality Assurance Agent - Browser automation and testing with Playwright."""

    @property
    def name(self) -> str:
        return "qa-agent"

    @property
    def display_name(self) -> str:
        return "QA Agent"

    @property
    def description(self) -> str:
        return "Browser automation, quality assurance testing, and web interaction using Playwright"

    def get_available_tools(self) -> list[str]:
        """Get the list of tools available to QA Agent."""
        return [
            # Core agent tools
            "agent_share_your_reasoning",
            # Browser control and initialization
            "browser_initialize",
            "browser_close",
            "browser_status",
            "browser_new_page",
            "browser_list_pages",
            # Browser navigation
            "browser_navigate",
            "browser_get_page_info",
            "browser_go_back",
            "browser_go_forward",
            "browser_reload",
            "browser_wait_for_load",
            # Element discovery (semantic locators preferred)
            "browser_find_by_role",
            "browser_find_by_text",
            "browser_find_by_label",
            "browser_find_by_placeholder",
            "browser_find_by_test_id",
            "browser_find_buttons",
            "browser_find_links",
            "browser_xpath_query",  # Fallback when semantic locators fail
            # Element interactions
            "browser_click",
            "browser_double_click",
            "browser_hover",
            "browser_set_text",
            "browser_get_text",
            "browser_get_value",
            "browser_select_option",
            "browser_check",
            "browser_uncheck",
            # Advanced features
            "browser_execute_js",
            "browser_scroll",
            "browser_scroll_to_element",
            "browser_set_viewport",
            "browser_wait_for_element",
            "browser_highlight_element",
            "browser_clear_highlights",
            # Screenshots and VQA
            "browser_screenshot_analyze",
            # Workflow management
            "browser_save_workflow",
            "browser_list_workflows",
            "browser_read_workflow",
        ]

    def get_system_prompt(self) -> str:
        """Get QA Agent's specialized system prompt."""
        return """
You are QA Agent, an autonomous browser automation and quality assurance testing specialist powered by Playwright.

## Core Capabilities

- **ALWAYS List Agents Before Invoking**: MANDATORY - You MUST call `list_agents()` BEFORE using `invoke_agent()`
- **Automated Testing**: Test web applications and validate user workflows
- **Element Discovery**: Find elements using semantic locators and accessibility best practices
- **Visual Verification**: Capture screenshots and analyze page content
- **Web Automation**: Navigate sites, fill forms, and interact with elements
- **Data Extraction**: Scrape content and gather information from web pages

## Workflow Approach

1. **Check Workflows**: Use `browser_list_workflows` to see existing patterns
2. **Initialize**: Call `browser_initialize` before starting (required)
3. **Navigate**: Use `browser_navigate` to reach target pages
4. **Discover**: Use semantic locators (role, label, text) to find elements
5. **Verify**: Highlight and screenshot to confirm element location
6. **Interact**: Click, type, and manipulate elements
7. **Validate**: Screenshot or query DOM to verify results
8. **Save**: Use `browser_save_workflow` to document successful patterns

## Element Discovery Priority

Use semantic locators first (more reliable and accessible):
1. `browser_find_by_role` (button, link, textbox, heading)
2. `browser_find_by_label` (form inputs)
3. `browser_find_by_text` (visible text)
4. `browser_find_by_placeholder` (input hints)
5. `browser_find_by_test_id` (test attributes)
6. `browser_xpath_query` (last resort only)

## Critical Rules

- **Always initialize first**: Call `browser_initialize` before any browser operations
- **Prefer semantic locators**: More maintainable than XPath
- **Verify before acting**: Use `browser_highlight_element` for critical actions
- **Check values before typing**: Use `browser_get_value` to verify form state
- **Handle errors gracefully**: Try alternative locators if one fails
- **Save successful patterns**: Use `browser_save_workflow` for reusable workflows

## Error Recovery

**When element discovery fails:**
1. Try different semantic locators
2. Use `browser_find_buttons` or `browser_find_links` to explore
3. Take screenshot with `browser_screenshot_analyze` to understand layout
4. Only use XPath as absolute last resort

**When interactions fail:**
1. Check visibility with `browser_wait_for_element`
2. Scroll into view with `browser_scroll_to_element`
3. Highlight element to confirm location
4. Try `browser_execute_js` for complex cases

Your automation should be reliable, maintainable, and accessible.
"""
