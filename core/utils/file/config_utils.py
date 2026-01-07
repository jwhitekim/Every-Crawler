import yaml
import os

# YAML 파일 읽기
def load_config(config_path="config/config.yaml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as file:
        return yaml.safe_load(file)
    
# YAML 파일에 키-값 저장
def save_config(data, config_path="config/config.yaml"):
    with open(config_path, "w") as file:
        yaml.dump(data, file)

class ConfigLoader:
    def __new__(cls, config_path="config/config.yaml"):
        # Create a temporary instance
        instance = super(ConfigLoader, cls).__new__(cls)
        instance.config = {}
        instance.load_env(config_path)
        return instance.config  # Return the config object directly

    def load_env(self, config_path):
        if not os.path.exists(config_path):
            return {}
        with open(config_path, "r") as file:
            return yaml.safe_load(file)