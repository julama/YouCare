import os
import docx2txt
import re

# Define the folder containing the .docx files
folder_path = '/Users/julian/PycharmProjects/YouCare/resources/korrigierte_docs/Vorsorge und Finanzierung'

# Loop through all .docx files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".docx"):
        # Convert .docx to plain text
        text = docx2txt.process(os.path.join(folder_path, filename))

        # Remove content in brackets and the brackets themselves
        text = re.sub(r'\([^)]*\)', '', text)

        # Split the text by lines
        lines = text.split('\n')

        # Extract the title (first non-empty line)
        title = None
        for line in lines:
            line = line.strip()
            if line:
                title = line
                break

        if title:
            # Remove the extracted title from the text
            text = '\n'.join(lines[1:])

            # Define the new .txt filename
            new_filename = os.path.splitext(filename)[0] + '.txt'

            # Write the modified text to a .txt file
            print(os.path.join(folder_path, new_filename))
            with open(os.path.join(folder_path, new_filename), 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)

print("Conversion and processing complete.")
