import os, logging
from datetime import datetime
from collections import deque

def read_logs(filename, encoding="utf-8", num_lines=None) -> str:
    try:
        with open(filename, 'r', encoding=encoding) as log_file:
            if num_lines is None:
                return log_file.read()
            else:
                return ''.join(deque(log_file, maxlen=num_lines))  # O(1) 메모리 최적화
    except FileNotFoundError:
        return f"Log file '{filename}' not found."
    except Exception as e:
        return f"Error reading log file: {e}"
        
class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        if not fmt:
            #fmt = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
            fmt = "%(asctime)s - %(levelname)s - %(relpath)s:%(lineno)d - %(funcName)s - %(message)s"
        super().__init__(fmt, datefmt, style, validate)  # 부모 클래스의 __init__ 호출

    def format(self, record):
        try:
            record.relpath = os.path.relpath(record.pathname)
        except ValueError:  # 경로가 잘못된 경우 대비
            record.relpath = record.pathname
        return super().format(record)
    
    def formatTime(self, record, datefmt=None):
        # 원하는 형식을 명시
        datefmt = datefmt or '%Y-%m-%d %H:%M:%S'  # Default: YYYY-MM-DD HH:MM:SS,ms
        ct = self.converter(record.created)  # 기본 시간 변환기 사용 (localtime)
        return datetime.fromtimestamp(record.created).strftime(datefmt)

class BaseFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding='utf-8'):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        super().__init__(filename, mode, encoding)

class CustomLogging(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.DEBUG)

    def addHandler(self, filename, fmt=None, mode='a', encoding='utf-8'):
        if filename is None:
            raise ValueError("filename cannot be None. A valid log file path is required.")
        for handler in self.handlers:
            if isinstance(handler, BaseFileHandler) and handler.baseFilename == os.path.abspath(filename):
                return
        handler = BaseFileHandler(filename, mode, encoding)
        handler.setFormatter(CustomFormatter(fmt))
        super().addHandler(handler)

class GetLogger:
    _instances = {}  # 여러 개의 싱글톤 인스턴스를 저장할 딕셔너리

    def __new__(cls, logger_type, logger_name=None, fmt=None, logger_option="GlobalLogger") -> CustomLogging:
        if logger_type not in cls._instances:
            logger = CustomLogging(logger_option)  # logger_option을 로거 이름으로 사용
            logger.addHandler(logger_name, fmt)
            cls._instances[logger_type] = logger  # 특정 타입의 로거 저장
        return cls._instances[logger_type]  # 동일한 타입의 로거 반환

if __name__=="__main__":
    logger = GetLogger(
        "logger", "src/logs/test.log", 
        "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
        )

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")