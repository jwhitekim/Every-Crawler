import time
import random
from typing import Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from core.everytime.exception import exception_handler
from core.utils.custom_logging import CustomLogging

@exception_handler
def login_everytime(
    browser: Chrome, 
    logger: CustomLogging,
    my_id: Optional[str], 
    my_password: Optional[str],
    wait_time: Optional[int] = None
) -> Optional[bool]:
    """Logs in to the website."""
    if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
        wait_time = random.uniform(2, 5)

    if not my_id or not my_password:
        logger.error("Everytime ID and Password are None")
        raise ValueError("Everytime credentials are missing")

    logger.info("Attempting to log in with ID: %s", my_id)

    try:
        if browser.find_element(By.CSS_SELECTOR, "div#submenu"):
            logger.info("Already logged in, skipping login process.")
            return False
    except NoSuchElementException:
        logger.warning("Not logged in, proceeding with login.")

    try:
        signin_button = browser.find_element(By.CSS_SELECTOR, "a.signin")
        logger.info("Sign-in button found, clicking...")
        signin_button.click()
    except NoSuchElementException:
        logger.warning("Sign-in button not found, skipping...")

    logger.info("Locating login form...")
    login_form = browser.find_element(By.CSS_SELECTOR, "form[method='post']")

    id_elem = login_form.find_element(By.NAME, "id")
    password_elem = login_form.find_element(By.NAME, "password")
    keep_checkbox = login_form.find_element(By.CLASS_NAME, "keep")

    logger.info("Entering credentials...")
    id_elem.send_keys(my_id)
    password_elem.send_keys(my_password)

    logger.info("Checking 'Keep me logged in' checkbox...")
    keep_checkbox.click()

    logger.info("Submitting login form...")
    password_elem.send_keys(Keys.ENTER)

    logger.info("Waiting for %s seconds after login attempt...", wait_time)
    time.sleep(wait_time)

    logger.info("Login process completed successfully.")
    return True


    
    
    

