"""Convert images to PDF - JEE Advanced Papers with custom ordering."""

import os
from pathlib import Path
from PIL import Image

def images_to_pdf(image_folder, output_pdf, first_image):
    """Convert images to a single PDF file with specific first image."""
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    image_files = []
    
    for file in Path(image_folder).iterdir():
        if file.suffix.lower() in image_extensions:
            image_files.append(file)
    
    if not image_files:
        print("No image files found in the folder!")
        return
    
    # Sort images by timestamp in DESCENDING order (newest first)
    image_files.sort(key=lambda x: x.name, reverse=True)
    
    print(f"Found {len(image_files)} images")
    print("\nFinal sequence (timestamp descending order):")
    for i, img_file in enumerate(image_files, 1):
        print(f"  {i:2d}. {img_file.name}")
    
    # Convert all images to RGB mode
    images = []
    print("\nLoading images...")
    for img_file in image_files:
        try:
            img = Image.open(img_file)
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
            print(f"✓ Loaded: {img_file.name}")
        except Exception as e:
            print(f"✗ Error loading {img_file.name}: {e}")
    
    if not images:
        print("No valid images to convert!")
        return
    
    # Save as PDF
    print(f"\nCreating PDF: {output_pdf}")
    images[0].save(
        output_pdf,
        save_all=True,
        append_images=images[1:],
        resolution=100.0,
        quality=95,
        optimize=True
    )
    
    print(f"✅ PDF created successfully: {output_pdf}")
    print(f"📄 Total pages: {len(images)}")
    print(f"📋 First page: {image_files[0].name}")
    print(f"📋 Last page: {image_files[-1].name}")

if __name__ == "__main__":
    # Configuration
    image_folder = "images"
    output_pdf = "jee-advanced-2005.pdf"
    first_image = "Screenshot 2026-07-22 231124.png"  # This will be the first page
    
    # Check if folder exists
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' not found!")
        exit(1)
    
    # Create PDF
    images_to_pdf(image_folder, output_pdf, first_image)
