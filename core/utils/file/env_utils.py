from dotenv import load_dotenv, set_key, dotenv_values
import os

# .env 파일 읽기
def load_env(dotenv_path="./.env"):
    load_dotenv(dotenv_path)
    return dotenv_values(dotenv_path)

# .env 파일에 키-값 저장
def save_env(key, value, dotenv_path=".env"):
    if not os.path.exists(dotenv_path):
        open(dotenv_path, "w").close()  # .env 파일이 없으면 생성
    set_key(dotenv_path, key, value)

class envLoader:
    def __new__(cls, dotenv_path=".env"):
        # Create a temporary instance
        instance = super(envLoader, cls).__new__(cls)
        instance.config = {}
        instance.load_env(dotenv_path)
        return instance.config  # Return the config object directly

    def load_env(self, dotenv_path=".env"):
        load_dotenv(dotenv_path=dotenv_path)
        self.config["my_id"] = os.getenv("my_id")
        self.config["my_password"] = os.getenv("my_password")