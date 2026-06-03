from google.genai import types
from .get_files_info import schema_get_files_info, get_files_info
from .get_file_content import schema_get_file_content, get_file_content
from .run_python_file import schema_run_python_file, run_python_file
from .write_file import schema_write_file, write_file
from collections.abc import Callable

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file
}

available_functions = types.Tool(
    function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file],
)

def call_function(
        function_call: types.FunctionCall,
        working_directory: str,
        verbose: bool = False,
) -> types.Content:
    
    function_name = function_call.name or ""

    args = dict(function_call.args) if function_call.args else {}

    if function_name not in function_map:
        return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"},
            )
        ],
    )

    args["working_directory"] = working_directory
    selected_function = function_map[function_name]
    function_result = selected_function(**args)

    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_name,
            response={"result": function_result}
        )
    ],
)