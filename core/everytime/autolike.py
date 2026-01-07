import time
import random
from typing import List, Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.everytime.exception import exception_handler
from core.everytime.everytime_utils import _navigate
from core.everytime.everytime_utils import _scroll_into_view
from core.everytime.everytime_utils import _initialize_articles
from core.utils.custom_logging import CustomLogging

class EverytimeAutoLiker:
    def __init__(self, browser: Chrome, logger: CustomLogging, start_article: str, page_num: int):
        self.logger = logger
        self.browser = browser
        self.start_article = start_article
        self.page_num = page_num
    
    @classmethod
    @exception_handler
    def start(cls, browser, logger, start_article, page_num):
        liker = cls(browser, logger, start_article, page_num)
        liker.run()

    def _create_art_list(self, articles: List[WebElement], comparison_str: str) -> List[str]:
        """Generates a list of article titles, stopping at the comparison string."""
        self.logger.info("Creating article list, stopping at: %s", comparison_str)

        art_list = []
        for article in articles:
            title = article.text.splitlines()[0]
            if comparison_str == title:
                break
            art_list.append(title)

        self.logger.info("Generated article list with %s articles", len(art_list))
        return art_list

    def _get_title_of_article(self, article: WebElement) -> str:
        """Returns the title of the given article."""
        return article.find_element(By.TAG_NAME, "h2").text

    def _click_alert(self, wait_time: Optional[int] = None) -> None:
        """Handles potential alerts after clicking like button."""
        if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
            wait_time = random.uniform(0.5, 1.5)

        try:
            alert = Alert(self.browser)
            self.logger.info("Alert detected, accepting...")
            alert.accept()

            time.sleep(wait_time)
            alert.accept()
            time.sleep(wait_time)

        except:
            self.logger.warning("No alert found.")
            pass

        finally:
            self.logger.info("Returning to the previous page.")
            self.browser.back()
            time.sleep(wait_time)

    def _like_button_click(self) -> None:
        """Clicks the like button and handles potential alerts."""
        try:
            like_button = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "posvote"))
            )
            _scroll_into_view(self.browser, like_button)
            like_button.click()

            self.logger.info("Like button clicked.")
            self._click_alert()
        except Exception as e:
            self.logger.error("Failed to click like button: %s", e)

    def _click_articles(self, article: WebElement, art_name: str, art_list: List[str], wait_time: Optional[int] = None) -> None:
        """Handles the liking of an individual article."""
        if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
            wait_time = random.uniform(2, 5)

        self.logger.info("Processing article: %s", art_name)
        
        _scroll_into_view(self.browser, article)
        article.click()
        self.logger.info("Clicked on article. Waiting for %s seconds before proceeding.", wait_time)
        time.sleep(wait_time)

        article_name = self.browser.find_element(By.XPATH, "//h2[@class='large']").text
        self.logger.info("Article click completed: <%s>", article_name)
        self._like_button_click()

        art_list.remove(art_name)
        self.logger.info("Removed %s from article list. Remaining articles: %s", art_name, len(art_list))

    def _repeat_article_likes(self, art_list: List[str], changed_name: str = None) -> None:
        """Iterates through articles and likes them."""
        while art_list:
            articles = _initialize_articles(self.browser)

            first_article = self._get_title_of_article(articles[0])
            if changed_name == first_article:
                self.logger.info("First article unchanged, stopping auto-like.")
                break

            self.logger.debug(
                "[First Article]: %s, [Articles Count]: %s, [Art List Count]: %s",
                first_article, len(articles), len(art_list)
            )

            for article in reversed(articles):
                changed_name = self._get_title_of_article(article)
                if changed_name in art_list:
                    self._click_articles(article, changed_name, art_list)
                    break  # 한 번 클릭하면 루프 종료

            if len(art_list) == 0:
                articles = _initialize_articles(self.browser)
                art_list = self._create_art_list(articles, changed_name)

    def run(self) -> None:
        """Likes articles from the starting point, navigating pages if necessary."""
        self.logger.info("Starting auto-like from article: %s, across %s pages", self.start_article, self.page_num)

        for index in range(self.page_num):
            articles = _initialize_articles(self.browser)
            art_list = self._create_art_list(articles, self.start_article)

            self.logger.debug("[Art List]: %s", ', '.join(art_list))

            self._repeat_article_likes(art_list)

            remaining_pages = self.page_num - index
            self.logger.info("20 articles clicked successfully, remaining pages: %s", remaining_pages)

            _navigate(self.browser, "prev")

