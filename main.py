from PIL import Image, ImageOps
import io
from typing import Tuple, Union, BinaryIO
import gc


from duotone import Duotone

class LambdaImageProcessor:
    """
    Lambda-optimized image processing functions with minimal memory footprint.
    """
    
    @staticmethod
    def convert_to_color_scale(image_data: Union[bytes, BinaryIO], 
                              color: Tuple[int, int, int] = (255, 0, 0),
                              blend: float = 0.5,
                              output_format: str = 'JPEG',
                              quality: int = 85) -> bytes:
        """
        Convert image to color scale with minimal memory usage.
        
        Args:
            image_data: Image byt   es or file-like object
            color: RGB color tuple for the color scale
            output_format: Output format ('JPEG', 'PNG', 'WEBP')
            quality: JPEG quality (1-100)
            
        Returns:
            bytes: Processed image as bytes
        """
        try:
            # Open image from bytes/stream
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            else:
                img = Image.open(image_data)
            
            # Convert to grayscale efficiently
            gray_img = ImageOps.grayscale(img)
            
            # Convert to RGB mode for color application
            rgb_img = gray_img.convert('RGB')
            
            # Apply color tint using PIL's built-in methods
            # Create a color image and use it as a mask
            color_layer = Image.new('RGB', rgb_img.size, color)
            
            # Use multiply blend mode for color tinting
            result_img = Image.blend(
                Image.new('RGB', rgb_img.size, (0, 0, 0)),
                color_layer,
                0.5
            )
            
            # Apply original luminance
            result_img = Image.composite(result_img, color_layer, gray_img)
            
            # Save to bytes
            output_buffer = io.BytesIO()
            save_kwargs = {'format': output_format}
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            result_img.save(output_buffer, **save_kwargs)
            
            # Clean up
            img.close()
            gray_img.close()
            rgb_img.close()
            result_img.close()
            gc.collect()
            
            output_buffer.seek(0)
            return output_buffer.getvalue()
            
        except Exception as e:
            raise RuntimeError(f"Color scale conversion failed: {str(e)}")
    
    @staticmethod
    def convert_to_duotone(image_data: Union[bytes, BinaryIO],
                          color1: Tuple[int, int, int] = (0, 0, 0),
                          color2: Tuple[int, int, int] = (255, 255, 255),
                          output_format: str = 'JPEG',
                          quality: int = 85) -> bytes:
        """
        Convert image to duotone with minimal memory usage.
        
        Args:
            image_data: Image bytes or file-like object
            color1: RGB color for shadows/dark areas
            color2: RGB color for highlights/light areas
            output_format: Output format
            quality: JPEG quality
            
        Returns:
            bytes: Processed image as bytes
        """
        try:
            # Open image
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            else:
                img = Image.open(image_data)
            
            
            result_img = Duotone.process(img, color1, color2)
            
            # Save to bytes
            output_buffer = io.BytesIO()
            save_kwargs = {'format': output_format}
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            result_img.save(output_buffer, **save_kwargs)
            
            # Clean up
            img.close()
            result_img.close()
            gc.collect()
            
            output_buffer.seek(0)
            return output_buffer.getvalue()
            
        except Exception as e:
            raise RuntimeError(f"Duotone conversion failed: {str(e)}")
    
    @staticmethod
    def clip_image(image_data: Union[bytes, BinaryIO],
                   bbox: Tuple[int, int, int, int] = None,
                   center_crop: bool = False,
                   target_size: Tuple[int, int] = None,
                   output_format: str = 'JPEG',
                   quality: int = 85) -> bytes:
        """
        Clip image with minimal memory usage.
        
        Args:
            image_data: Image bytes or file-like object
            bbox: Bounding box (left, top, right, bottom)
            center_crop: If True, crop from center to target_size
            target_size: Target size (width, height) for center crop
            output_format: Output format
            quality: JPEG quality
            
        Returns:
            bytes: Processed image as bytes
        """
        try:
            # Open image
            if isinstance(image_data, bytes):
                img = Image.open(io.BytesIO(image_data))
            else:
                img = Image.open(image_data)
            
            width, height = img.size
            
            if bbox:
                # Validate and crop using bounding box
                left, top, right, bottom = bbox
                left = max(0, min(left, width))
                top = max(0, min(top, height))
                right = max(left, min(right, width))
                bottom = max(top, min(bottom, height))
                
                result_img = img.crop((left, top, right, bottom))
                
            elif center_crop and target_size:
                # Center crop to target size
                target_width, target_height = target_size
                
                # Calculate center crop coordinates
                left = (width - target_width) // 2
                top = (height - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                
                # Ensure bounds
                if right > width or bottom > height:
                    scale = min(width / target_width, height / target_height)
                    new_width = int(target_width * scale)
                    new_height = int(target_height * scale)
                    
                    left = (width - new_width) // 2
                    top = (height - new_height) // 2
                    right = left + new_width
                    bottom = top + new_height
                
                result_img = img.crop((left, top, right, bottom))
                
            else:
                # Default: 10% margin crop
                margin_x = int(width * 0.1)
                margin_y = int(height * 0.1)
                result_img = img.crop((margin_x, margin_y, 
                                     width - margin_x, height - margin_y))
            
            # Save to bytes
            output_buffer = io.BytesIO()
            save_kwargs = {'format': output_format}
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            result_img.save(output_buffer, **save_kwargs)
            
            # Clean up
            img.close()
            result_img.close()
            gc.collect()
            
            output_buffer.seek(0)
            return output_buffer.getvalue()
            
        except Exception as e:
            raise RuntimeError(f"Image clipping failed: {str(e)}")

# Lambda handler example
def lambda_handler(event, context):
    """
    AWS Lambda handler example for image processing.
    """
    import base64
    import json
    
    try:
        # Parse request
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        
        # Get image data (base64 encoded)
        image_b64 = body.get('image')
        operation = body.get('operation', 'color_scale')
        
        if not image_b64:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No image data provided'})
            }
        
        # Decode image
        image_data = base64.b64decode(image_b64)
        
        # Initialize processor
        processor = LambdaImageProcessor()
        
        # Process based on operation
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
        
        # Return processed image as base64
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

# Batch processing function for multiple images
def process_batch(images_data: list, operation: str, **kwargs) -> list:
    """
    Process multiple images efficiently.
    
    Args:
        images_data: List of image bytes
        operation: Processing operation
        **kwargs: Operation parameters
        
    Returns:
        List of processed image bytes
    """
    processor = LambdaImageProcessor()
    results = []
    
    for image_data in images_data:
        try:
            if operation == 'color_scale':
                result = processor.convert_to_color_scale(image_data, **kwargs)
            elif operation == 'duotone':
                result = processor.convert_to_duotone(image_data, **kwargs)
            elif operation == 'clip':
                result = processor.clip_image(image_data, **kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            results.append(result)
            
        except Exception as e:
            results.append(None)  # or handle error as needed
    
    return results

# Example usage for local testing
if __name__ == "__main__":
    # Test with local file
    processor = LambdaImageProcessor()
    
    # Read image file
    with open("input/000001.jpg", "rb") as f:
        image_data = f.read()
    
    # Process
    result = processor.convert_to_color_scale(image_data, (200, 200, 200))
    
    # Save result
    with open("output/000001.jpg", "wb") as f:
        f.write(result)
    
    print("Processing complete!")