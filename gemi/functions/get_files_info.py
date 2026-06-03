import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory: str, directory: str = ".") -> str:

    '''
    Two vars used to get the absolute path of your working directory
    so the AI agent can't access files outside your working directory
    scope
    '''

    abs_path = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(abs_path, directory))

    # print(f"Working Directory is: {abs_path}") | Test case

    # Checks if it's the target directory is equal to the abs path
    valid_target_dir = os.path.commonpath([abs_path, target_dir]) == abs_path

    try:

        if valid_target_dir: # if truthy return the path
            if os.path.isdir(target_dir):

                items = os.listdir(target_dir)

                lines = []
                
                for file in items:

                    full_path = os.path.join(target_dir, file)
                    size = os.path.getsize(full_path)
                    is_dir = os.path.isdir(full_path)
            
                    name = f"- {file}: file_size={size} bytes, is_dir={is_dir}"
                    lines.append(name)
                
                return "\n".join(lines)
                
            else:
                return (f'Error: "{directory}" is not a directory')

        else:
            return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(get_files_info())