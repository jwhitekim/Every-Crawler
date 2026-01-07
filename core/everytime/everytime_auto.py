from selenium.common.exceptions import NoSuchElementException
from core.everytime.articles import move_to_board, find_starting_point
from core.everytime.autolike import EverytimeAutoLiker
from core.everytime.login import login_everytime
from core.utils.custom_logging import GetLogger
from core.utils.file.env_utils import load_env
from core.utils.chrome_manager import ChromeDriverService

class RunEverytimeAutoLike(ChromeDriverService):
    def __init__(self, headless, logging_file_path="app.log"):
        super().__init__()
        self.logging_file_path = logging_file_path
        self.logger = GetLogger("logger_everytime", logging_file_path)
        self.start_running(headless)
        
    def get_id_password(self):
        # .env 파일 및 config.yaml 파일 불러오기
        env_values = load_env()

        # .env에서 민감한 정보 가져오기
        my_id = env_values.get("EVERYTIME_USERNAME")
        my_password = env_values.get("EVERYTIME_PASSWORD")
        
        self.logger.info("Everytime ID, Password: %s, %s", my_id, my_password)
        
        if not my_id or not my_password:
            self.logger.error("Everytime ID, Password are missing in .env file!")
            raise

        return my_id, my_password
    
    def start_running(self, headless):
        self.logger.info("Starting Everytime auto-like...")
        
        try:
            self.start(headless=headless, url="https://everytime.kr/")

            # 크롬이 종료되었을 경우 예외 처리
            if not self.browser:
                self.logger.error("Chrome browser failed to start.")
                raise SystemExit("Chrome browser failed to start.")

            login_everytime(self.browser, self.logger, *self.get_id_password())
            move_to_board(self.browser, self.logger, "자유게시판")
            start_article, page_num = find_starting_point(self.browser, self.logger, self.logging_file_path)

            self.logger.info("Starting from article: %s, page number: %s", start_article, page_num)

            EverytimeAutoLiker.start(self.browser, self.logger, start_article, page_num)

        except NoSuchElementException:
            self.logger.error("Exiting program as there are no more elements to process.")
            raise 

        finally:
            self.stop()
            self.logger.info("The task is complete.")
            return 