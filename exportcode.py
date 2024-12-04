import os

def export_code():
    code_files = []
    exclude_dirs = ['.venv', 'venv', '__pycache__', '.git']

    for root, dirs, files in os.walk('.'):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and file != 'export_code.py':
                code_files.append(os.path.join(root, file))

    all_code = ''
    for file_path in code_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            all_code += f"\n# {'-'*20}\n# File: {file_path}\n# {'-'*20}\n\n{code}\n"

    with open('all_code_output.txt', 'w', encoding='utf-8') as f:
        f.write(all_code)

    print("All code has been exported to all_code_output.txt")

if __name__ == "__main__":
    export_code()
