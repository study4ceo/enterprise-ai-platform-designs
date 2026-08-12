#!/usr/bin/env python3
"""
Convert Markdown documentation to styled PDFs
"""
import os
import glob
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Custom CSS for professional styling
PDF_STYLE = """
@page {
    size: A4;
    margin: 2cm;
    
    @top-center {
        content: "AI/ML Interview Prep Guide";
        font-size: 10pt;
        color: #666;
    }
    
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #999;
    }
}

body {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}

h1 {
    color: #2c3e50;
    font-size: 28pt;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 1em;
    border-bottom: 3px solid #3498db;
    padding-bottom: 0.3em;
    page-break-after: avoid;
}

h2 {
    color: #34495e;
    font-size: 20pt;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.7em;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 0.2em;
    page-break-after: avoid;
}

h3 {
    color: #555;
    font-size: 16pt;
    font-weight: bold;
    margin-top: 1.2em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h4 {
    color: #666;
    font-size: 13pt;
    font-weight: bold;
    margin-top: 1em;
    margin-bottom: 0.4em;
}

/* Code blocks */
pre {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-left: 4px solid #3498db;
    padding: 1em;
    overflow-x: auto;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    line-height: 1.4;
    border-radius: 4px;
    page-break-inside: avoid;
}

code {
    background: #f1f3f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    color: #e83e8c;
}

pre code {
    background: transparent;
    padding: 0;
    color: #333;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background: #3498db;
    color: white;
    padding: 0.7em;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 0.7em;
    border: 1px solid #dee2e6;
}

tr:nth-child(even) {
    background: #f8f9fa;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #3498db;
    padding-left: 1em;
    margin-left: 0;
    color: #555;
    font-style: italic;
    background: #f8f9fa;
    padding: 0.5em 1em;
    border-radius: 4px;
}

/* Lists */
ul, ol {
    margin: 0.5em 0;
    padding-left: 2em;
}

li {
    margin: 0.3em 0;
}

/* Links */
a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Horizontal rules */
hr {
    border: none;
    border-top: 2px solid #e0e0e0;
    margin: 2em 0;
}

/* Badges/Labels */
.badge {
    display: inline-block;
    padding: 0.2em 0.5em;
    font-size: 9pt;
    font-weight: bold;
    border-radius: 3px;
    margin-right: 0.3em;
}

.badge-success {
    background: #28a745;
    color: white;
}

.badge-warning {
    background: #ffc107;
    color: #333;
}

.badge-danger {
    background: #dc3545;
    color: white;
}

/* Checkboxes (✅ ❌) */
.emoji {
    font-size: 12pt;
}

/* Page breaks */
.page-break {
    page-break-after: always;
}

/* Cover page */
.cover {
    text-align: center;
    padding-top: 5cm;
    page-break-after: always;
}

.cover h1 {
    font-size: 36pt;
    border: none;
    margin-bottom: 1em;
}

.cover .subtitle {
    font-size: 18pt;
    color: #666;
    margin-bottom: 2em;
}

.cover .date {
    font-size: 12pt;
    color: #999;
}

/* TOC */
.toc {
    page-break-after: always;
}

.toc h2 {
    text-align: center;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin: 0.5em 0;
    padding-left: 1em;
}

/* Syntax highlighting hints */
.keyword { color: #0000ff; font-weight: bold; }
.string { color: #a31515; }
.comment { color: #008000; font-style: italic; }
.function { color: #795e26; }
"""

def create_cover_page(title, subtitle="AI/ML Interview Preparation"):
    """Create a cover page"""
    from datetime import datetime
    
    html = f"""
    <div class="cover">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        <p class="date">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    """
    return html

def markdown_to_html(md_file):
    """Convert markdown to HTML with styling"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Configure markdown extensions
    extensions = [
        'markdown.extensions.extra',      # Tables, fenced code, etc.
        'markdown.extensions.codehilite', # Syntax highlighting
        'markdown.extensions.toc',        # Table of contents
        'markdown.extensions.nl2br',      # Newline to <br>
        'markdown.extensions.sane_lists', # Better list handling
    ]
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=extensions,
        extension_configs={
            'codehilite': {
                'linenums': False,
                'guess_lang': False,
            }
        }
    )
    
    # Get title from first H1
    title = Path(md_file).stem.replace('-', ' ').title()
    
    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html, title

def convert_md_to_pdf(md_file, output_dir='pdfs'):
    """Convert single markdown file to PDF"""
    
    print(f"Converting: {md_file}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert markdown to HTML
    html_content, title = markdown_to_html(md_file)
    
    # Output PDF path
    pdf_name = Path(md_file).stem + '.pdf'
    pdf_path = os.path.join(output_dir, pdf_name)
    
    # Configure fonts
    font_config = FontConfiguration()
    
    # Create PDF
    html = HTML(string=html_content)
    css = CSS(string=PDF_STYLE, font_config=font_config)
    
    html.write_pdf(
        pdf_path,
        stylesheets=[css],
        font_config=font_config
    )
    
    print(f"✅ Created: {pdf_path}")
    return pdf_path

def convert_all_docs(pattern='*.md', output_dir='pdfs'):
    """Convert all markdown files to PDFs"""
    
    md_files = glob.glob(pattern)
    
    # Exclude README.md (convert last)
    md_files = [f for f in md_files if 'README' not in f]
    
    if not md_files:
        print("No markdown files found!")
        return
    
    print(f"\nFound {len(md_files)} markdown files")
    print("="*60)
    
    pdf_files = []
    
    for md_file in sorted(md_files):
        try:
            pdf_path = convert_md_to_pdf(md_file, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {md_file}: {e}")
    
    # Convert README last
    readme_files = glob.glob('README*.md')
    for readme in readme_files:
        try:
            pdf_path = convert_md_to_pdf(readme, output_dir)
            pdf_files.append(pdf_path)
        except Exception as e:
            print(f"❌ Error converting {readme}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ Converted {len(pdf_files)} files to PDF")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    print("="*60)
    
    return pdf_files

def create_combined_pdf(md_files, output_file='Interview-Prep-Guide-Complete.pdf'):
    """Create single combined PDF from multiple markdown files"""
    
    print("\nCreating combined PDF...")
    
    # Combine all HTML
    combined_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI/ML Interview Preparation Guide</title>
    </head>
    <body>
    """
    
    # Add cover page
    combined_html += create_cover_page(
        "AI/ML Interview Preparation Guide",
        "Complete Documentation"
    )
    
    # Add each document
    for i, md_file in enumerate(sorted(md_files), 1):
        print(f"Adding: {md_file}")
        
        html_content, title = markdown_to_html(md_file)
        
        # Extract body content
        import re
        body_match = re.search(r'<body>(.*)</body>', html_content, re.DOTALL)
        if body_match:
            combined_html += f'<div class="page-break"></div>\n'
            combined_html += f'<h1 style="page-break-before: always;">Part {i}: {title}</h1>\n'
            combined_html += body_match.group(1)
    
    combined_html += """
    </body>
    </html>
    """
    
    # Create PDF
    font_config = FontConfiguration()
    html = HTML(string=combined_html)
    css = CSS(string=PDF_STYLE, font_config=font_config)
    
    html.write_pdf(
        output_file,
        stylesheets=[css],
        font_config=font_config
    )
    
    print(f"✅ Combined PDF created: {output_file}")
    return output_file

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert markdown docs to styled PDFs')
    parser.add_argument('--pattern', default='*.md', help='Glob pattern for markdown files')
    parser.add_argument('--output-dir', default='pdfs', help='Output directory for PDFs')
    parser.add_argument('--combined', action='store_true', help='Create single combined PDF')
    parser.add_argument('--file', help='Convert single file')
    
    args = parser.parse_args()
    
    if args.file:
        # Convert single file
        convert_md_to_pdf(args.file, args.output_dir)
    else:
        # Convert all files
        pdf_files = convert_all_docs(args.pattern, args.output_dir)
        
        # Create combined PDF if requested
        if args.combined:
            md_files = glob.glob(args.pattern)
            md_files = [f for f in md_files if 'README' not in f]
            create_combined_pdf(md_files)
