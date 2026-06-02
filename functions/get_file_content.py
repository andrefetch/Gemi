import os
from config import MAX_CHARS

def get_file_content(working_directory: str, file_path: str) -> str:

    abs_path = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(abs_path, file_path))

    valid_file = os.path.commonpath([abs_path, target_path]) == abs_path

    try:
        if not valid_file:  
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        
        elif not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        else:
            with open(target_path) as f:

                content = f.read(MAX_CHARS)

                if f.read(1):

                    content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

                return content

    except Exception as e:
        return f'Error: {e}'
