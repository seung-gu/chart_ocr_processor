"""Script to visualize various image preprocessing techniques."""

import cv2
import numpy as np
from pathlib import Path


def apply_preprocessing_techniques(image_path: Path, output_dir: Path):
    """Apply various preprocessing techniques and save results."""
    # Read image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Cannot read image: {image_path}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Original image
    cv2.imwrite(str(output_dir / '00_original.png'), image)
    print("Original image saved")
    
    # 2. Grayscale conversion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(output_dir / '01_grayscale.png'), gray)
    print("Grayscale conversion completed")
    
    # 3. OTSU binarization
    _, otsu_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(str(output_dir / '02_otsu_binary.png'), otsu_binary)
    print(f"OTSU binarization completed (threshold: {_})")
    
    # 4. OTSU binarization (inverted)
    _, otsu_binary_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cv2.imwrite(str(output_dir / '03_otsu_binary_inv.png'), otsu_binary_inv)
    print("OTSU binarization (inverted) completed")
    
    # 5. Adaptive threshold
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    cv2.imwrite(str(output_dir / '04_adaptive_threshold.png'), adaptive_thresh)
    print("Adaptive threshold completed")
    
    # 6. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_gray = clahe.apply(gray)
    cv2.imwrite(str(output_dir / '05_clahe.png'), clahe_gray)
    print("CLAHE completed")
    
    # 7. Histogram equalization
    hist_eq = cv2.equalizeHist(gray)
    cv2.imwrite(str(output_dir / '06_histogram_equalization.png'), hist_eq)
    print("Histogram equalization completed")
    
    # 8. Gaussian blur
    gaussian_blur = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite(str(output_dir / '07_gaussian_blur.png'), gaussian_blur)
    print("Gaussian blur completed")
    
    # 9. Denoising (Non-local Means Denoising)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    cv2.imwrite(str(output_dir / '08_denoised.png'), denoised)
    print("Denoising completed")
    
    # 10. Morphology operation (Closing)
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(otsu_binary, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite(str(output_dir / '09_morphology_closing.png'), closing)
    print("Morphology operation (Closing) completed")
    
    # 11. Morphology operation (Opening)
    opening = cv2.morphologyEx(otsu_binary, cv2.MORPH_OPEN, kernel)
    cv2.imwrite(str(output_dir / '10_morphology_opening.png'), opening)
    print("Morphology operation (Opening) completed")
    
    # 12. CLAHE + OTSU
    clahe_otsu = clahe.apply(gray)
    _, clahe_otsu_binary = cv2.threshold(clahe_otsu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(str(output_dir / '11_clahe_otsu.png'), clahe_otsu_binary)
    print("CLAHE + OTSU completed")
    
    # 13. Denoising + OTSU
    denoised_otsu = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    _, denoised_otsu_binary = cv2.threshold(denoised_otsu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(str(output_dir / '12_denoised_otsu.png'), denoised_otsu_binary)
    print("Denoising + OTSU completed")
    
    # 14. Histogram equalization + OTSU
    hist_eq_otsu = cv2.equalizeHist(gray)
    _, hist_eq_otsu_binary = cv2.threshold(hist_eq_otsu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(str(output_dir / '13_hist_eq_otsu.png'), hist_eq_otsu_binary)
    print("Histogram equalization + OTSU completed")
    
    print(f"\nAll preprocessing results saved to {output_dir}")


if __name__ == '__main__':
    test_image = Path('output/estimates/20161209-6.png')
    output_dir = Path('output/preprocessing_test/image_preprocessing')
    
    apply_preprocessing_techniques(test_image, output_dir)
