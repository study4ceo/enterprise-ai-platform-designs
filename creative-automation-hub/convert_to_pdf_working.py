#!/usr/bin/env python3
"""
Convert Markdown documentation to PDFs using reportlab
"""
import os
import glob
from pathlib import Path
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from html.parser import HTMLParser

class HTMLToReportlab(HTMLParser):
    """Convert HTML to reportlab flowables"""
    
    def __init__(self, styles):
        super().__init__()
        self.styles = styles
        self.story = []
        self.current_text = []
        self.current_style = 'Normal'
        self.in_code = False
        self.in_pre = False
        self.pre_text = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.current_style = 'Heading1'
        elif tag == 'h2':
            self.current_style = 'Heading2'
        elif tag == 'h3':
            self.current_style = 'Heading3'
        elif tag == 'h4':
            self.current_style = 'Heading4'
        elif tag == 'code':
            self.in_code = True
        elif tag == 'pre':
            self.in_pre = True
            self.pre_text = []
        elif tag == 'p':
            self.current_style = 'Normal'
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('<b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('<i>')
        elif tag == 'br':
            self.current_text.append('<br/>')
            
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'p']:
            if self.current_text:
                text = ''.join(self.current_text).strip()
                if text:
                    self.story.append(Paragraph(text, self.styles[self.current_style]))
                    self.story.append(Spacer(1, 0.2*inch))
                self.current_text = []
            self.current_style = 'Normal'
        elif tag == 'code':
            self.in_code = False
        elif tag == 'pre':
            self.in_pre = False
            if self.pre_text:
                code_text = ''.join(self.pre_text)
                self.story.append(Preformatted(code_text, self.styles['Code']))
                self.story.append(Spacer(1, 0.2*inch))
                self.pre_text = []
        elif tag == 'strong' or tag == 'b':
            self.current_text.append('</b>')
        elif tag == 'em' or tag == 'i':
            self.current_text.append('</i>')
            
    def handle_data(self, data):
        if self.in_pre:
            self.pre_text.append(data)
        elif self.in_code:
            self.current_text.append(f'<font name="Courier">{data}</font>')
        else:
            self.current_text.append(data)

def setup_styles():
    """Create custom styles"""
    styles = getSampleStyleSheet()
    
    # Modify existing styles - black text only
    styles['Heading1'].fontSize = 24
    styles['Heading1'].textColor = colors.black
    styles['Heading1'].spaceAfter = 12
    styles['Heading1'].spaceBefore = 12
    
    styles['Heading2'].fontSize = 18
    styles['Heading2'].textColor = colors.black
    styles['Heading2'].spaceAfter = 10
    styles['Heading2'].spaceBefore = 10
    
    styles['Heading3'].fontSize = 14
    styles['Heading3'].textColor = colors.black
    styles['Heading3'].spaceAfter = 8
    styles['Heading3'].spaceBefore = 8
    
    styles['Heading4'].fontSize = 12
    styles['Heading4'].textColor = colors.black
    styles['Heading4'].spaceAfter = 6
    styles['Heading4'].spaceBefore = 6
    
    # Code style - black text
    styles['Code'].fontSize = 9
    styles['Code'].fontName = 'Courier'
    styles['Code'].textColor = colors.black
    styles['Code'].backColor = colors.white
    styles['Code'].borderWidth = 1
    styles['Code'].borderColor = colors.black
    styles['Code'].borderPadding = 10
    styles['Code'].leftIndent = 10
    styles['Code'].rightIndent = 10
    styles['Code'].spaceAfter = 10
    styles['Code'].spaceBefore = 10
    
    return styles

def markdown_to_pdf(md_file, output_dir='pdfs'):
    """Convert markdown file to PDF"""
    
    print(f"Converting: {md_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'nl2br', 'sane_lists']
    )
    
    # Output PDF path
    pdf_name = Path(md_file).stem + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_name)
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    
    # Setup styles
    styles = setup_styles()
    
    # Parse HTML and create story
    parser = HTMLToReportlab(styles)
    parser.feed(html_content)
    story = parser.story
    
    if not story:
        # Fallback: add raw markdown as preformatted text
        story = [
            Paragraph(Path(md_file).stem.replace('-', ' ').title(), styles['Heading1']),
            Spacer(1, 0.3*inch),
            Preformatted(md_content, styles['Code'])
        ]
    
    # Build PDF
    doc.build(story)
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ Created: {pdf_path} ({file_size:,} bytes)")
    return pdf_path

def convert_all_docs(pattern='*.md', output_dir='pdfs'):
    """Convert all markdown files to PDFs"""
    
    md_files = glob.glob(pattern)
    
    # Exclude README initially
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
            pdf_path = markdown_to_pdf(md_file, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {md_file}: {e}")
            import traceback
            traceback.print_exc()
    
    # Convert README last
    for readme in sorted(readme_files):
        try:
            pdf_path = markdown_to_pdf(readme, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {readme}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"✅ Converted {len(pdf_files)}/{len(md_files)} files to PDF")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    print("="*60)
    
    return pdf_files

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert markdown docs to PDFs')
    parser.add_argument('--pattern', default='*.md', help='Glob pattern')
    parser.add_argument('--output-dir', default='pdfs', help='Output directory')
    parser.add_argument('--file', help='Convert single file')
    
    args = parser.parse_args()
    
    if args.file:
        markdown_to_pdf(args.file, args.output_dir)
    else:
        convert_all_docs(args.pattern, args.output_dir)
