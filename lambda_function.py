from PIL import Image, ImageOps
import io
from typing import Tuple, Union, BinaryIO
import gc
import base64
import json

def convert_to_color_scale(
    image_data: Union[bytes, BinaryIO], 
    color: Tuple[int, int, int] = (255, 0, 0),
    blend: float = 0.5,
    output_format: str = 'JPEG',
    quality: int = 85
) -> bytes:
    try:
        if isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            img = Image.open(image_data)
        
        gray_img = ImageOps.grayscale(img)
        rgb_img = gray_img.convert('RGB')
        color_layer = Image.new('RGB', rgb_img.size, color)
        result_img = Image.blend(
            Image.new('RGB', rgb_img.size, (0, 0, 0)),
            color_layer,
            0.5
        )
        result_img = Image.composite(result_img, color_layer, gray_img)
        
        
        output_buffer = io.BytesIO()
        save_kwargs = {'format': output_format}
        if output_format == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        result_img.save(output_buffer, **save_kwargs)
        
        img.close()
        gray_img.close()
        rgb_img.close()
        result_img.close()
        gc.collect()
        output_buffer.seek(0)
        return output_buffer.getvalue()
    except Exception as e:
        raise RuntimeError(f"Color scale conversion failed: {str(e)}")

def lambda_handler(event, context):
    """
    AWS Lambda handler example for image processing.
    """
    import base64
    import json
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        
        image_b64 = body.get('image')
        operation = body.get('operation', 'color_scale')
        
        if not image_b64:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data provided'})
            }
        
        image_data = base64.b64decode(image_b64)
        
        processor = LambdaImageProcessor()
        
        if operation == 'color_scale':
            color = tuple(body.get('color', [255, 0, 0]))
            result = processor.convert_to_color_scale(image_data, color)
        elif operation == 'duotone':
            color1 = tuple(body.get('color1', [0, 0, 0]))
            color2 = tuple(body.get('color2', [255, 255, 255]))
            result = processor.convert_to_duotone(image_data, color1, color2)
        elif operation == 'clip':
            bbox = body.get('bbox')
            center_crop = body.get('center_crop', False)
            target_size = body.get('target_size')
            if target_size:
                target_size = tuple(target_size)
            result = processor.clip_image(image_data, bbox, center_crop, target_size)  
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid operation'})
            }
        
        result_b64 = base64.b64encode(result).decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'image': result_b64,
                'operation': operation
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }