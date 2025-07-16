from base64 import b64encode
import json
import os
import requests
from PIL import Image
from io import BytesIO

API_ENDPOINT = 'https://haptgydvz1.execute-api.us-east-1.amazonaws.com/dev'
INPUT_DIR = 'input'

def test_with_input(input_id: str):
    path = os.path.join(INPUT_DIR, input_id)
    if not os.path.isfile(path):
        print('[ERROR] Invalid input test file')
        return

    with open(path, 'rb') as img_file:
        encoded = b64encode(img_file.read()).decode('utf-8')
    
    # Create the JSON payload that matches what your Lambda expects
    payload = {
        'body': encoded  # This is the format your Lambda expects
    }
    
    r = requests.post(
        url=API_ENDPOINT,
        data=encoded.tobytes(),
    )

    print(f"Status code: {r.status_code}")
    print(f"Response headers: {r.headers}")
    print(f"Response text: {r.text}")

    # Only try to parse JSON if you got a 200 response
    if r.status_code == 200:
        try:
            result = r.json()
            print(f"Success: {result}")
            
            # If you want to save the result image:
            if 'image' in result:
                from base64 import b64decode
                output_img_data = b64decode(result['image'])
                output_img = Image.open(BytesIO(output_img_data))
                output_img.save(f'output_{input_id}')
                print(f'[SUCCESS] Output image saved as output_{input_id}')
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {r.text}")
    else:
        print(f"HTTP error: {r.status_code}")

test_with_input('000001.jpg')