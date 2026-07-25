# JEE Advanced Papers - Image to PDF Converter

Convert images of JEE Advanced question papers into a single PDF file.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a folder named `2005` and place your images inside it

3. Run the script:
```bash
python create_pdf.py
```

## How It Works

1. **Automatic Sorting**: Images are sorted by numbers in their filenames
2. **Sequence Detection**: Extracts numbers from filenames (e.g., `page1.jpg`, `page2.jpg`)
3. **PDF Generation**: Combines all images into `jee-advanced-2005.pdf`
4. **Quality**: High-quality PDF with optimization

## Image Naming Tips

For best results, name your images with numbers:
- `page1.jpg`, `page2.jpg`, `page3.jpg`
- `001.jpg`, `002.jpg`, `003.jpg`
- `question_1.png`, `question_2.png`

The script will automatically detect and sort by these numbers.

## Supported Formats

- JPG/JPEG
- PNG
- BMP
- TIFF
- GIF

## Output

- **File**: `jee-advanced-2005.pdf`
- **Location**: Same directory as the script
- **Quality**: High resolution (100 DPI), optimized
