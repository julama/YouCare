import os
import shutil

directory_path = '/Users/julian/PycharmProjects/YouCare/resources/docs/HK'

# Get the list of .txt files in the specified directory
txt_files = [filename for filename in os.listdir(directory_path) if filename.endswith('.txt')]

# Create a list to store Page objects
pages = []

# Iterate over each .txt file
for txt_file in txt_files:
    # Create the new .py filename
    py_filename = f"coach_{txt_file[:-4]}.py"

    # Copy the coach_template.py file to the new .py filename
    shutil.copy(f'{directory_path}/coach_template.py', py_filename)

    # Replace the variable name in the copied .py file with the .txt filename
    with open(py_filename, 'r') as file:
        file_contents = file.read()
        file_contents = file_contents.replace('name = "Abklärung und Diagnose"', f'name = "{txt_file[:-4]}"')

    # Write the modified contents back to the .py file
    with open(py_filename, 'w') as file:
        file.write(file_contents)

    # Create a Page object and add it to the list
    pages.append(f'Page("pages/{py_filename}", "{txt_file[:-4]}")')

# Print the list of Page objects
print('[' + ',\n'.join(pages) + ']')