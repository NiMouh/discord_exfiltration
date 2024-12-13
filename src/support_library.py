import os
from dotenv import load_dotenv
from random import randint

DISCORD_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
DISCORD_MIN_FILE_SIZE = 1 * 1024 * 1024  # 1 MB

def get_token(token_name : str) -> str:
    load_dotenv()

    if token_name not in os.environ:
        raise ValueError(f"Environment variable {token_name} not found.")

    return os.getenv(token_name)

def split_file(file_path: str, chunk_size: int = DISCORD_MAX_FILE_SIZE, min_chunk_size: int = DISCORD_MIN_FILE_SIZE) -> None:
    """
    Split a large file into smaller chunks with random sizes.
    
    Args:
        file_path (str): The path to the file to be split.
        chunk_size (int): The maximum size of any chunk (default: DISCORD_MAX_FILE_SIZE).
        min_chunk_size (int): The minimum size of any chunk (default: 1MB).
    """
    if min_chunk_size > chunk_size:
        raise ValueError("min_chunk_size cannot be greater than chunk_size.")
    
    with open(file_path, 'rb') as f:
        chunk_number = 0
        while True:
            # Generate a random size between min_chunk_size and chunk_size
            random_size = randint(min_chunk_size, chunk_size)
            chunk = f.read(random_size)
            if not chunk:
                break
            
            # Write the chunk to a new file
            chunk_file_path = f"{file_path}.part{chunk_number}"
            with open(chunk_file_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            print(f"Created: {chunk_file_path} with size {len(chunk) / 1024 ** 2:.2f} MB.")
            chunk_number += 1
    
    print(f"File split into {chunk_number} parts.")

def gather_files(path: str) -> list:
    """
    Gather all files in the specified path.
    
    Args:
        path (str): The path to the directory containing files.
    
    Returns:
        list: A list of file paths.
    """

    if not os.path.exists(path):
        print(f"ERROR: Path {path} does not exist.")
        return []

    file_paths = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if not os.path.isfile(file_path):
            continue

        if os.path.getsize(file_path) < DISCORD_MAX_FILE_SIZE:
            file_paths.append(file_path)
            continue

        split_file(file_path)
        for part in os.listdir(path):
            part_path = os.path.join(path, part)
            if not part.startswith(file + ".part"):
                continue
            file_paths.append(part_path)

    return file_paths

def clean_files(path: str) -> None:
    """
    Clean up the files that were split.
    
    Args:
        path (str): The path to the directory containing files.
    """
    for file in os.listdir(path):
        if ".part" not in file:
            continue

        file_path = os.path.join(path, file)
        os.remove(file_path)

    print("All split files cleaned up.")
