from google.genai import types
from .get_files_info import schema_get_files_info
from .get_file_content import schema_get_file_content
from .run_python_file import schema_run_python_file
from .write_file import schema_write_file

available_functions = types.Tool(
    function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file],
)