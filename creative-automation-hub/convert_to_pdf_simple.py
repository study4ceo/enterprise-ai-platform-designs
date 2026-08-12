#!/usr/bin/env python3
"""
Convert Markdown documentation to styled PDFs using markdown-pdf
"""
import os
import glob
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

def convert_md_to_pdf(md_file, output_dir='pdfs'):
    """Convert single markdown file to PDF"""
    
    print(f"Converting: {md_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Output PDF path
    pdf_name = Path(md_file).stem + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_name)
    
    # Create PDF
    pdf = MarkdownPdf()
    
    # Configure styling
    pdf.meta = {
        "title": Path(md_file).stem.replace('-', ' ').title(),
        "author": "AI/ML Interview Prep"
    }
    
    # Add markdown content
    pdf.add_section(Section(md_file))
    
    # Write PDF
    pdf.save(pdf_path)
    
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def convert_all_docs(pattern='*.md', output_dir='pdfs'):
    """Convert all markdown files to PDFs"""
    
    md_files = glob.glob(pattern)
    
    # Exclude README.md initially
    main_files = [f for f in md_files if 'README' not in f]
    readme_files = [f for f in md_files if 'README' in f]
    
    if not md_files:
        print("No markdown files found!")
        return []
    
    print(f"\nFound {len(md_files)} markdown files")
    print("="*60)
    
    pdf_files = []
    
    # Convert main docs
    for md_file in sorted(main_files):
        try:
            pdf_path = convert_md_to_pdf(md_file, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {md_file}: {e}")
    
    # Convert README files last
    for readme in sorted(readme_files):
        try:
            pdf_path = convert_md_to_pdf(readme, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {readme}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ Converted {len(pdf_files)}/{len(md_files)} files to PDF")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    print("="*60)
    
    return pdf_files

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert markdown docs to styled PDFs')
    parser.add_argument('--pattern', default='*.md', help='Glob pattern for markdown files')
    parser.add_argument('--output-dir', default='pdfs', help='Output directory for PDFs')
    parser.add_argument('--file', help='Convert single file')
    
    args = parser.parse_args()
    
    if args.file:
        # Convert single file
        convert_md_to_pdf(args.file, args.output_dir)
    else:
        # Convert all files
        pdf_files = convert_all_docs(args.pattern, args.output_dir)
        
        print("\n📄 Generated PDFs:")
        for pdf in pdf_files:
            print(f"  - {pdf}")
