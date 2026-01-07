import re
from typing import Optional
import subprocess
import chromedriver_autoinstaller
from selenium_stealth import stealth
import os, socket, shlex, platform, traceback
from selenium.webdriver import Chrome, ChromeOptions

def find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # OS가 사용 가능한 포트를 자동 할당
        return s.getsockname()[1]

def find_chrome_path(CHROME_PATHS) -> Optional[str]:
    """CHROME_PATHS 중 존재하는 실행 파일 경로를 반환"""
    return next((path for path in CHROME_PATHS if os.path.exists(path)), None)

def get_user_agent():
    system = platform.system()
    if system == "Windows":
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    elif system == "Linux":
        return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    elif system == "Darwin":  # MacOS
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"

class ChromeProcessManager:
    # Chrome 실행 경로 목록
    CHROME_PATHS = [
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    ]

    CHROME_OPTIONS = [
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--log-level=3",
        "--user-data-dir=C:\\chrometemp"
    ]
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port: Optional[int] = None
    
    @property
    def paths(self):
        return self.CHROME_PATHS
    
    @paths.setter
    def paths(self, value):
        self.CHROME_PATHS = value

    @property
    def options(self):
        return self.CHROME_OPTIONS
    
    @options.setter
    def options(self, value):
        self.CHROME_OPTIONS = value

    def start_chrome(self, headless: bool, available_port: int):
        self.port = available_port
        chrome_path = find_chrome_path(self.CHROME_PATHS)
        chrome_command = [chrome_path] + self.CHROME_OPTIONS
        chrome_command.append(f"--remote-debugging-port={available_port}")
        if headless:
            chrome_command.append("--headless")
        self.process = subprocess.Popen(chrome_command)

    def stop_chrome(self):
        if platform.system() != "Windows":
            print("[Debug] Non-Windows: Using simple terminate().")
            if self.process:
                self.process.terminate()
            self.process = None
            return

        if not self.port:
            print("[Debug] No port stored. Cannot find process to kill via port.")
            # 혹시 모르니 self.process라도 종료 시도
            if self.process:
                print(f"[Debug] Fallback: Terminating self.process (PID: {self.process.pid})")
                self.process.terminate() # 기본 terminate
            self.process = None
            return

        print(f"[Debug] Finding process using port: {self.port}")
        
        try:
            # 1. netstat으로 포트를 사용하는 PID 찾기
            # 'LISTENING' 상태의 프로세스를 찾습니다.
            cmd = f'netstat -aon | findstr "LISTENING" | findstr ":{self.port}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='cp949')
            output = result.stdout.strip()
            
            if not output:
                print(f"[Debug] No process found listening on port {self.port}.")
                return

            print(f"[Debug] netstat output: {output}")

            # 2. netstat 출력에서 PID 파싱 (가장 마지막 숫자)
            pid_found = None
            match = re.findall(r'\d+$', output.splitlines()[0].strip()) # 첫 번째 줄의 마지막 숫자
            if match:
                pid_found = match[0]
                print(f"[Debug] Found PID {pid_found} using port {self.port}.")
            
            if not pid_found:
                print(f"[Debug] Could not parse PID from netstat output.")
                return

            # 3. 찾은 PID로 taskkill 실행 (/T로 자식까지 모두)
            print(f"[Debug] Killing process tree for PID: {pid_found}")
            kill_cmd = ['taskkill', '/F', '/T', '/PID', pid_found]
            kill_result = subprocess.run(kill_cmd, capture_output=True, text=True, encoding='cp949')
            
            if kill_result.returncode == 0:
                print(f"[Debug] taskkill success: {kill_result.stdout.strip()}")
            else:
                # "프로세스를 찾을 수 없습니다" 등의 오류
                print(f"[Debug] taskkill error: {kill_result.stderr.strip()}")

        except Exception as e:
            print(f"[Debug] Error during port-based kill: {e}")
        finally:
            self.process = None
            self.port = None # 포트 정리

class WebDriverController:
    def __init__(self):
        self.browser: Optional["Chrome"] = None

    def start_driver(self, available_port: int):
        chromedriver_autoinstaller.install()
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{available_port}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={get_user_agent()}")
        self.browser = Chrome(options=options)

    def navigate_to(self, url, maximize, wait):  
        self.browser.get(url)
        if maximize:
            self.browser.maximize_window()
        self.browser.implicitly_wait(wait)
       
    def quit_driver(self):
        if self.browser:
            self.browser.quit() 
            self.browser = None  # WebDriver 정리


class AdvancedStealthService:
    def __init__(self, stealth_config=None):
        self.stealth_config = stealth_config or {
            "languages": ["en-US", "en"],
            "vendor": "Google Inc.",
            "platform": "Win32",
            "webgl_vendor": "Intel Inc.",
            "renderer": "Intel Iris OpenGL Engine",
            "fix_hairline": True
        }

    def apply_stealth(self, browser):
        self._apply_stealth_library(browser, self.stealth_config)
        self._apply_additional_stealth(browser)

    def _apply_stealth_library(self, browser, stealth_config):
        stealth(browser, **stealth_config)

    def _apply_additional_stealth(self, browser: Chrome):
        scripts = [
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            "window.navigator.chrome = {runtime: {}};",
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
        ]

        for script in scripts:
            browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
            
class ChromeDriverService(WebDriverController):
    def __init__(self, args=None, paths=None, stealth_config=None):
        self.process_manager: ChromeProcessManager = ChromeProcessManager()
        self.stealth_manager: AdvancedStealthService = AdvancedStealthService(stealth_config)
        super().__init__()

        if args is not None:
            if isinstance(args, str):
                self.process_manager.options = shlex.split(args)
            elif isinstance(args, list):
                self.process_manager.options = args
            else:
                raise TypeError("paths must be a list of strings")
        
        if paths is not None:
            if isinstance(paths, list):
                self.process_manager.paths = paths
            else:
                raise TypeError("paths must be a string")
            
    def __enter__(self) -> "ChromeDriverService":
        return self  # 객체 자체를 반환

    def __exit__(self, exc_type, exc_value, traceback_obj) -> bool:      
        self.stop()  # 안전한 종료 처리
        
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, traceback_obj)
        
            if exc_type is KeyboardInterrupt:
                return True  # Ctrl+C 예외 무시
            
        return False  # 예외를 다시 발생시켜 상위 코드에서 처리할 수 있도록 함.

    def start(self, url, headless: bool, maximize: bool = True, wait: int = 3):
        available_port = find_available_port()
        self.process_manager.start_chrome(headless, available_port)
        self.start_driver(available_port)
        self.navigate_to(url, maximize, wait)
        self.stealth_manager.apply_stealth(self.browser)

    def stop(self):
        self.quit_driver()
        self.process_manager.stop_chrome()


    