import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs python files in a specified directory relative to the working directory, does not run if not a py file or one of the errors.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="This is the file path that is relative to the working directory, this is where you run at.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description='This is an optional argument for running python files'
            )
        },
    ),
)

def run_python_file(
        working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    
    abs_path = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(abs_path, file_path))

    valid_file = os.path.commonpath([abs_path, target_path]) == abs_path

    try:
        if not valid_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        elif not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        elif not target_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ['python', target_path]

        if args:
            command.extend(args)
        
        completed_process = subprocess.run(command, cwd=abs_path, capture_output=True, text=True, timeout=30)

        output = []

        if completed_process.returncode != 0:
            output.append(f"Process exited with code {completed_process.returncode}")
        elif (not completed_process.stdout) and (not completed_process.stderr):
            output.append("No output produced")
        elif completed_process.stdout:
            output.append(f'STDOUT: {completed_process.stdout}')
        elif completed_process.stderr:
            output.append(f'STDERR: {completed_process.stderr}')
        
        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"