import time, random
from enum import Enum
from typing import Union
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement   

class ScrollBehavior(Enum):
    AUTO = "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });"
    SMOOTH = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });"
    END = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end' });"

def _initialize_articles(browser: Chrome):
    return browser.find_elements(By.XPATH, "//article[@class='list']")

def _navigate(
    browser: Chrome, 
    direction: str, 
    wait_time: Union[int, float, None] = None
) -> None:
    """Navigates to the next or previous page."""
    if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
        wait_time = random.uniform(1, 2)

    if direction not in {"prev", "next"}:
        raise ValueError(f"Invalid direction '{direction}'. Expected 'prev' or 'next'.")

    pagination = browser.find_element(By.CLASS_NAME, "pagination")
    button = pagination.find_element(By.CLASS_NAME, direction)
    _scroll_into_view(browser, button)
    button.click()
    time.sleep(wait_time)
    
def _scroll_into_view(
    browser: Chrome, 
    element: WebElement,
    scroll_script: str = ScrollBehavior.AUTO.value,  
    wait_time: Union[int, float, None] = None
) -> None:
    """Scrolls the browser to bring the element into view."""
    if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
        wait_time = random.uniform(1, 2)
    
    browser.execute_script(scroll_script, element)
    time.sleep(wait_time)