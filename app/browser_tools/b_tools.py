from langchain.tools import tool
from playwright.async_api import Page
from pathlib import Path

def create_browser_tools(page:Page):

    @tool
    async def open_page( url: str) -> str:
        """Open an HTTP or HTTPS webpage and return its title."""
        
        if not url.startswith(("http", "https")):
            return "Error: only http or https urls are allowed."
        
        try: 
            web_page= await page.goto(url,  wait_until="domcontentloaded")
            return f"Page Opened: {await web_page.title()}"
        except Exception as e:
            return f"Could not opened page: {e}"
        
        
    @tool
    async def close_page()-> str:
        """Close an opened page."""
        
        if not page.is_closed():
            await page.close()
            return "Success: page has closed"
        
        return "Warning: Page is already closed"
        
        

    @tool
    async def get_page_title() -> str:
        """Get the title of the current browser page."""
        try:
            title = await page.title()
            return f"Page title: {title}"
        except Exception as e:
            return f"Failed to get page title: {e}"

    @tool
    async def get_current_url() -> str:
        """Get the current page URL."""
        try:
            return f"Current URL: {page.url}"
        except Exception as e:
            return f"Failed to get current URL: {e}"
        
    @tool
    async def refresh_page() -> str:
        """Refresh the current browser page."""
        try:
            await page.reload(wait_until="domcontentloaded", timeout=30000)
            return f"Refreshed page: {page.url}"
        except Exception as e:
            return f"Failed to refresh page: {e}"
        
        
    @tool
    async def click_element( selector:str) -> str:
        """Click an element using playwright css selector"""
        
        try:
            await page.locator(selector).click(timeout= 10000)
            return f"Clicked element: {selector}"
        except Exception as e:
            return f"Failed to click element {selector}: {str(e)}"
    
        
    @tool
    async def press_key( key:str)-> str:
        """Press keyboard key on current web page: 
        for example- Tab, Enter, Shift, ArrowDown, Control+A, Escape"""
        
        try:
            await page.keyboard.press(key)
            return f"Successfully pressed key: {key}"
        except Exception as e:
            return f"Failed to press key {key}: {str(e)}"
        

    @tool
    async def press_key_on_element(
        
        selector: str,
        key: str
    ) -> str:
        """Focus an element and press a key on it using a CSS selector."""
        try:
            element = page.locator(selector)
            await element.wait_for(state="visible", timeout=5000)
            await element.press(key)
            return f"Pressed {key} on element: {selector}"
        except Exception as e:
            return f"Failed to press {key}: {str(e)}"
        
        
    @tool
    async def type_text( selector:str, text:str) -> str:
        """Type text into an input text field or text area specified by CSS selector"""
        
        try:
            locator= page.locator(selector)
            await locator.fill(text, timeout= 10000)
            
            return f"Entered text into input field: {selector}"
            
        except Exception as e:
            return f"Failed to type text into input field {selector}: {str(e)}"
    
    @tool
    async def get_page_text(max_chars: int = 3000) -> str:
        """Read the visible text of the current page."""
        try:
            text = await page.inner_text("body")
            return text[:max(100, min(max_chars, 8000))]
        except Exception as e:
            return f"Could not read page text: {e}"
    
    @tool
    async def select_dropdown_option(
        
        selector: str,
        value: str,
    ) -> str:
        """Select an option by its value in a native HTML select dropdown."""
        try:
            await page.locator(selector).select_option(value=value)
            return f"Selected value '{value}' in {selector}"
        except Exception as e:
            return f"Dropdown selection failed: {e}"

    @tool
    async def check_checkbox( selector: str) -> str:
        """Check a checkbox or radio button."""
        try:
            await page.locator(selector).check(timeout=10000)
            return f"Checked: {selector}"
        except Exception as e:
            return f"Check failed: {e}"

    @tool
    async def uncheck_checkbox(selector: str) -> str:
        """Uncheck a checkbox."""
        try:
            await page.locator(selector).uncheck(timeout=10000)
            return f"Unchecked: {selector}"
        except Exception as e:
            return f"Uncheck failed: {e}"

    @tool
    async def scroll_page( direction: str, amount: int = 600) -> str:
        """Scroll the page up or down by a specified number of pixels."""
        try:
            if direction not in {"up", "down"}:
                return "Direction must be 'up' or 'down'."

            distance = max(1, min(amount, 5000))
            if direction == "up":
                distance = -distance

            await page.evaluate(
                "(distance) => window.scrollBy(0, distance)", distance
            )
            return f"Scrolled {direction} by {abs(distance)} pixels."
        except Exception as e:
            return f"Scrolling failed: {e}"

    @tool
    async def list_interactive_elements(max_items: int = 60) -> str:
        """List visible buttons, links, inputs, and selects to help identify selectors."""
        try:
            elements = await page.locator(
                'button, a, input, textarea, select, '
                '[role="button"], [role="textbox"], '
                '[contenteditable="true"]'
            ).evaluate_all(
                """els => els.filter(el => {
                    const r = el.getBoundingClientRect();
                    const s = getComputedStyle(el);

                    return r.width > 0 &&
                        r.height > 0 &&
                        s.visibility !== 'hidden' &&
                        s.display !== 'none';
                }).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    text: (
                        el.innerText ||
                        el.value ||
                        el.getAttribute('aria-label') ||
                        el.getAttribute('placeholder') ||
                        ''
                    ).trim().slice(0, 120),
                    id: el.id || null,
                    name: el.getAttribute('name'),
                    role: el.getAttribute('role'),
                    placeholder: el.getAttribute('placeholder'),
                    contenteditable: el.getAttribute('contenteditable')
                }))"""
            )
            limit = max(1, min(max_items, 100))
            return str(elements[:limit])
        except Exception as e:
            return f"Could not list interactive elements: {e}"

    @tool
    async def take_screenshot(path: str = "browser_screenshot.png") -> str:
        """Save a screenshot of the current page to a file."""
        try:
            destination = Path(path)
            if not destination.is_absolute():
                destination = Path.cwd() / destination

            destination.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(
                path=str(destination),
                full_page=False,
            )
            return f"Screenshot saved to: {destination}"
        except Exception as e:
            return f"Screenshot failed: {e}"
    
    @tool
    async def ask_human_to_help(reason: str) -> str:
        """Pause and ask the human to do something manually in the browser,
        such as solving a verification check or logging in."""
        print(f"\n[HUMAN NEEDED] {reason}")
        await asyncio.to_thread(input, "Press Enter here when you're done...")
        return "The human finished the manual step. Continue."
        
    @tool
    async def go_back()-> str:
        """Go back to the previous page in browser history"""
        
        try:
            response= await page.go_back(wait_until="domcontentloaded", timeout= 30000)
            if response is None:
                return f"Could not navigated back: no previous page in browser history."
            return f"Navigated back to page: {page.url}"
        except Exception as e:
            return f"Failed to go back: {str(e)}"
    
        
    @tool
    async def go_forward()-> str:
        """Navigate to the next page in browser history"""
        
        try:
            response = await page.go_forward(wait_until="domcontentloaded", timeout= 30000)
            if response is None:
                return f"Could not go forward: no next page in the browser history"
            return f"In browser history, navigated to the next page {page.url}"
        
        except Exception as e:
            return f"failed to go forward in browser history: {str(e)}"
        

    
    browser_tools_list=[
        open_page,
        close_page,
        get_page_title,
        click_element,
        go_forward,
        go_back,
        get_current_url,
        take_screenshot,
        list_interactive_elements,
        select_dropdown_option,
        scroll_page,
        uncheck_checkbox,
        type_text,
        check_checkbox,
        refresh_page,
        press_key,
        press_key_on_element,
        get_page_text,
        ask_human_to_help,
        
    ]
    
    return browser_tools_list