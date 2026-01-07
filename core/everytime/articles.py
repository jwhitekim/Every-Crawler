import re
import time
import random
from typing import Optional, List
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from core.everytime.everytime_utils import _navigate
from core.everytime.everytime_utils import _scroll_into_view
from core.everytime.everytime_utils import _initialize_articles
from core.everytime.exception import exception_handler
from core.utils.custom_logging import read_logs
from core.utils.custom_logging import CustomLogging


def _find_first_article(
    logger: CustomLogging,
    filename, 
    encoding: str = "utf-8", 
    num_lines: Optional[int] = None, 
    pattern: Optional[str] = None
) -> Optional[str]:
    """Finds the starting article for automation."""

    logger.info("Reading logs to find the starting article...")

    try:
        strLogs: str = read_logs(filename, encoding, num_lines)
        if not strLogs:
            logger.error("Log file is empty or missing.")
            return None
        
        found_count = 0
        start_article = []

        for row in reversed(strLogs.splitlines()):
            match = re.search(pattern, row)
            if match:
                start_article_text = match.group(1)
                logger.info("Found the starting point for likes in logs: %s", start_article_text)
                start_article.append(start_article_text)
                found_count += 1
                if found_count >= 5:
                    return start_article
        logger.warning("No matching articles found in logs.")
        return None
    
    except Exception as e:
        logger.error("Error while finding the first article: %s", e)
        return None


def _find_article_for_click(
    browser: Chrome, 
    logger: CustomLogging,
    start_article: List[str], 
    default_forward_pages: int = 3, 
    max_page_limit: int = 10
) -> tuple[str, int]:
    
    """Finds the article to start liking from."""

    if start_article:
        found = False
        page_num = 1
        logger.info("Searching for starting article: %s", ', '.join(start_article))

        while not found:
            articles = _initialize_articles(browser)
            for article in articles:
                _scroll_into_view(browser, article)
                article_text = article.find_element(By.TAG_NAME, "h2").text
                found_word = next((word for word in start_article if word == article_text), None)

                if found_word:
                    logger.info("Found matching article: %s", found_word)
                    found = True
                    break

            if found or page_num >= max_page_limit:
                break

            page_num += 1
            logger.info("Moving to page %s...", page_num)
            _navigate(browser, "next")
        return found_word, page_num
    
    else:
        logger.info("No starting article found, navigating %s pages forward...", default_forward_pages - 1)
        any(_navigate(browser, "next") for _ in range(default_forward_pages - 1))

        return None, default_forward_pages

@exception_handler
def move_to_board(
    browser: Chrome, 
    logger: CustomLogging, 
    board_name: str, 
    wait_time: Optional[int] = None
    ) -> None:
    """Navigates to the specified article board."""

    logger.info("Navigating to board: %s", board_name)

    if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
        wait_time = random.uniform(2, 5)

    submenu = browser.find_element(By.ID, "submenu")
    a_tags = submenu.find_elements(By.TAG_NAME, "a")
    
    for a_tag in a_tags:
        if a_tag.text == board_name:
            logger.info("Board '%s' found, clicking...", board_name)
            a_tag.click()
            logger.info("Waiting for %s seconds after navigation...", wait_time)
            time.sleep(wait_time)
            return
    
    logger.warning("Board '%s' not found!", board_name)

@exception_handler
def find_starting_point(
    browser: Chrome, 
    logger: CustomLogging,
    filename, 
    encoding: str = "utf-8", 
    num_lines: Optional[int] = None, 
    pattern: str = r"Article click completed: <([^<>]+)>",
    default_forward_pages: int = 10, 
    max_page_limit: int = 3
) -> "_find_article_for_click":
    """
    Combines find_first_article and find_article_for_click into a single function.
    """

    logger.info("Finding the starting point for auto-liking articles...")

    start_article = _find_first_article(logger, filename, encoding, num_lines, pattern)
    if start_article:
        logger.info("Starting article found: %s", ', '.join(start_article))
    else:
        logger.warning("No starting article found, starting from the first available page.")

    return _find_article_for_click(browser, logger, start_article, default_forward_pages, max_page_limit)