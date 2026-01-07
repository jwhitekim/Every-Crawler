import os
import hashlib

valid_extensions = (".jpg", ".jpeg", ".png", ".mp4", ".avi")  # 허용할 파일 확장자

def calculate_file_hash(file_path):
    """파일의 MD5 해시를 계산."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk:= f.read(8192):  # 8KB 단위로 파일 읽기
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicate_files(folder_path="D:/insta_download"):
    """
    폴더 내 중복 파일 제거.
    - folder_path: 탐색할 폴더 경로
    - valid_extensions: 처리할 파일 확장자 목록
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return
    
    file_hashes = {}
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 파일 확장자 확인
            if not file_name.lower().endswith(valid_extensions):
                continue

            file_hash = calculate_file_hash(file_path)

            # 중복된 파일이 이미 기록된 경우 삭제
            if file_hash in file_hashes:
                print(f"Duplicate found: {file_path} (same as {file_hashes[file_hash]})")
                os.remove(file_path)
            else:
                # 해시값과 파일 경로를 기록
                file_hashes[file_hash] = file_path

    print("Duplicate removal completed.")