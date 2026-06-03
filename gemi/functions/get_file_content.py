import os
from ..config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Grabs the file content of the targeted file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Grabs the file contents from the working directory can't exceed from the MAX_CHARS and then returns the content after reading the file.",
            ),
        },
    ),
)

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
