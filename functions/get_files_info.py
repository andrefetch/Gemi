import os

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
                return f'Success: "{directory}" is within the working directory'
            else:
                return (f'Error: "{directory}" is not a directory')

        else:
            return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print(get_files_info())