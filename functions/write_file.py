import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes to files in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="This is the absolute path to the file you would want to write to overwrite to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="This is what you write to, this is what will get written to the file thats in the file_path."
            )
        },
    ),
)

def write_file(working_directory: str, file_path: str, content: str) -> str:

    abs_path = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(abs_path, file_path))

    valid_file = os.path.commonpath([abs_path, target_path]) == abs_path

    try:
        if not valid_file:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        elif os.path.isdir(target_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        else:
            parent_dir = os.path.dirname(target_path)
            os.makedirs(parent_dir, exist_ok=True)

            with open(target_path, 'w') as f:
                f.write(content)

            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f'Error: {e}'
