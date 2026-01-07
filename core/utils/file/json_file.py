import json

JSON_FILE = "config/Location_Info.json"

def save_json(new_data):
    # 저장 시 튜플을 리스트로 변환
    with open(JSON_FILE, "w") as f:
        json.dump(new_data, f, indent=4)
    print(f"{JSON_FILE}에 데이터가 저장되었습니다.")

def load_json():
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def append_json(new_data):
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
            # 기존 데이터 리스트를 튜플 리스트로 변환
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # 새로운 데이터 추가 (중복 방지)
    if new_data not in data:
        data.append(new_data)

    # 저장 시 튜플을 리스트로 변환
    with open(JSON_FILE, "w") as f:
        json.dump(new_data, f, indent=4)
    print(f"{JSON_FILE}에 데이터가 저장되었습니다.")