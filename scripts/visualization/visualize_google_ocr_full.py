"""Script to perform full image OCR using Google Cloud Vision API and display text."""

from pathlib import Path
import cv2
import numpy as np
import os
from dotenv import load_dotenv

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("Warning: google-cloud-vision not available. Install with: uv add google-cloud-vision")

# Load environment variables from .env file
load_dotenv()


def visualize_google_ocr_full(image_path: Path, output_path: Path):
    """Perform full image OCR using Google Cloud Vision API and display text."""
    # Read image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Cannot read image: {image_path}")
        return
    
    if not GOOGLE_VISION_AVAILABLE:
        print("Google Cloud Vision is not installed.")
        return
    
    # Initialize Google Cloud Vision
    try:
        # Check key file path from .env file
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not creds_path:
            print("Google Cloud Vision authentication required.")
            print("Add the following to your .env file:")
            print("  GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-key.json")
            return
        
        # Check if it's a JSON file path
        if not creds_path.endswith('.json') or not Path(creds_path).exists():
            print(f"Error: Key file not found: {creds_path}")
            return
        
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        google_client = vision.ImageAnnotatorClient(credentials=credentials)
        print(f"Google Cloud Vision authentication completed: {creds_path}")
        print("Google Cloud Vision initialization completed")
    except Exception as e:
        print(f"Google Cloud Vision initialization failed: {e}")
        return
    
    # Perform Google Vision API OCR on full image
    print("\n=== Processing full image OCR with Google Cloud Vision ===")
    
    try:
        # Convert image to bytes
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()
        
        # Call Google Vision API (full image)
        vision_image = vision.Image(content=image_bytes)
        response = google_client.text_detection(image=vision_image)
        
        if response.error.message:
            print(f"Google Vision API error: {response.error.message}")
            return
        
        # Create result image
        img_result = image.copy()
        ocr_results = []
        
        if response.text_annotations:
            # First result is full text
            full_text = response.text_annotations[0].description
            print(f"\nFull recognized text:\n{full_text[:500]}...")  # Print first 500 characters only
            
            # Rest are individual word/text regions
            for i, annotation in enumerate(response.text_annotations[1:], 1):
                vertices = annotation.bounding_poly.vertices
                
                # Extract bounding box coordinates
                points = []
                for vertex in vertices:
                    points.append([vertex.x, vertex.y])
                
                if len(points) >= 3:
                    text = annotation.description
                    confidence = getattr(annotation, 'confidence', 1.0)
                    
                    ocr_results.append({
                        'index': i,
                        'text': text,
                        'bbox': points,
                        'confidence': confidence
                    })
                    
                    # Draw box
                    pts = np.array(points, dtype=np.int32)
                    cv2.polylines(img_result, [pts], True, (0, 255, 0), 2)
                    
                    # Display text
                    if points:
                        x, y = int(points[0][0]), int(points[0][1])
                        display_text = text[:30] if len(text) > 30 else text
                        cv2.putText(img_result, display_text, (x, y - 5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
        
        # Save
        cv2.imwrite(str(output_path), img_result)
        print(f"\nGoogle Cloud Vision visualization results saved to {output_path}")
        
        # Print results
        print(f"\n=== Google Cloud Vision Results (Total: {len(ocr_results)}) ===")
        for result in ocr_results[:50]:  # Print first 50 only
            print(f"{result['index']:3d}. '{result['text']}' (confidence: {result['confidence']:.2f})")
        
        if len(ocr_results) > 50:
            print(f"... and {len(ocr_results) - 50} more")
            
    except Exception as e:
        print(f"Google OCR error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_image = Path('output/estimates/20161209-6.png')
    output_path = Path('output/preprocessing_test/20161209-6_google_ocr_full.png')
    
    visualize_google_ocr_full(test_image, output_path)
