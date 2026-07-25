"""Convert images to PDF - JEE Advanced Papers with manual ordering."""

import os
from pathlib import Path
from PIL import Image
import re

def extract_number(filename):
    """Extract number from filename for sorting."""
    # Try to find numbers in the filename
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[-1])  # Use last number (time component)
    return 0

def show_images_preview(image_files):
    """Show list of images for manual ordering."""
    print("\n" + "="*80)
    print("CURRENT IMAGE ORDER:")
    print("="*80)
    for i, img_file in enumerate(image_files, 1):
        print(f"  {i:2d}. {img_file.name}")
    print("="*80 + "\n")

def manual_reorder(image_files):
    """Allow manual reordering of images."""
    print("MANUAL REORDERING")
    print("-" * 80)
    print("Enter the sequence you want (e.g., '1,3,2,4,5' or '1-5,10,6-9')")
    print("Or press ENTER to keep current order")
    print("Type 'subject' to organize by subject (Physics, Chemistry, Math)")
    print("-" * 80)
    
    choice = input("Your choice: ").strip().lower()
    
    if choice == '':
        return image_files
    
    if choice == 'subject':
        return organize_by_subject(image_files)
    
    try:
        # Parse the sequence
        new_order = []
        for part in choice.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                new_order.extend(range(start, end + 1))
            else:
                new_order.append(int(part))
        
        # Reorder images
        reordered = [image_files[i-1] for i in new_order if 0 < i <= len(image_files)]
        return reordered
    except Exception as e:
        print(f"Error parsing sequence: {e}")
        print("Keeping original order...")
        return image_files

def organize_by_subject(image_files):
    """Organize images by subject: Physics, Chemistry, Mathematics."""
    print("\n" + "="*80)
    print("ORGANIZE BY SUBJECT")
    print("="*80)
    
    subjects = {
        'physics': [],
        'chemistry': [],
        'mathematics': []
    }
    
    show_images_preview(image_files)
    
    print("For each image, enter the subject:")
    print("  P = Physics")
    print("  C = Chemistry")
    print("  M = Mathematics")
    print("  S = Skip this image")
    print("-" * 80)
    
    for i, img_file in enumerate(image_files, 1):
        while True:
            subject = input(f"Image {i} ({img_file.name}): ").strip().upper()
            if subject == 'P':
                subjects['physics'].append(img_file)
                break
            elif subject == 'C':
                subjects['chemistry'].append(img_file)
                break
            elif subject == 'M':
                subjects['mathematics'].append(img_file)
                break
            elif subject == 'S':
                break
            else:
                print("Invalid input! Use P, C, M, or S")
    
    # Combine in order: Physics -> Chemistry -> Mathematics
    ordered_images = subjects['physics'] + subjects['chemistry'] + subjects['mathematics']
    
    print("\n" + "="*80)
    print("NEW ORDER (Physics → Chemistry → Mathematics):")
    print("="*80)
    for i, img_file in enumerate(ordered_images, 1):
        if i <= len(subjects['physics']):
            subject = "Physics"
        elif i <= len(subjects['physics']) + len(subjects['chemistry']):
            subject = "Chemistry"
        else:
            subject = "Mathematics"
        print(f"  {i:2d}. [{subject:11s}] {img_file.name}")
    print("="*80 + "\n")
    
    confirm = input("Proceed with this order? (Y/n): ").strip().lower()
    if confirm == 'n':
        return image_files
    
    return ordered_images

def images_to_pdf(image_folder, output_pdf):
    """Convert images to a single PDF file."""
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    image_files = []
    
    for file in Path(image_folder).iterdir():
        if file.suffix.lower() in image_extensions:
            image_files.append(file)
    
    if not image_files:
        print("No image files found in the folder!")
        return
    
    # Sort images by timestamp
    image_files.sort(key=lambda x: extract_number(x.name))
    
    print(f"Found {len(image_files)} images")
    show_images_preview(image_files)
    
    # Ask user if they want to reorder
    reorder = input("Do you want to reorder the images? (Y/n): ").strip().lower()
    if reorder != 'n':
        image_files = manual_reorder(image_files)
    
    # Convert all images to RGB mode and collect them
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

if __name__ == "__main__":
    # Configuration
    image_folder = "images"  # Folder containing images
    output_pdf = "jee-advanced-2005.pdf"
    
    # Check if folder exists
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' not found!")
        print("Please create the folder and add images to it.")
        exit(1)
    
    # Create PDF
    images_to_pdf(image_folder, output_pdf)
