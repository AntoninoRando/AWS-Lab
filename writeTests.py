import os
from base64 import b64encode

input_folder = 'input'
output_file = 'tests.json'

with open(output_file, 'w') as out_file:
    out_file.write('[')

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as img_file:
            encoded = b64encode(img_file.read()).decode('utf-8')
            with open(output_file, 'a') as out_file:
                out_file.write(f'{{"body": "{encoded}"}},\n')

with open(output_file, 'a') as out_file:
    out_file.write(']')