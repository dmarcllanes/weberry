import os
import re

TEMPLATES_DIR = "templates"

def sanitize_html(content):
    # Remove script tags and their content
    content = re.sub(r'<script\b[^>]*>([\s\S]*?)</script>', '', content, flags=re.IGNORECASE)
    # Remove single line script tags if any
    content = re.sub(r'<script\b[^>]*/>', '', content, flags=re.IGNORECASE)
    return content

def sanitize_css(css_content, html_content):
    imports = []
    
    # Extract @import rules
    import_matches = re.findall(r'@import\s+(?:url\()?["\']?(.*?)["\']?\)?\s*;', css_content, flags=re.IGNORECASE)
    for url in import_matches:
        # Clean up URL
        url = url.strip('"\'')
        if url.startswith("url("):
            url = url[4:].strip(")'\"")
        imports.append(url)
    
    # Remove @import rules from CSS
    # Robust regex to handle semicolons inside the URL string (common in Google Fonts)
    # Matches @import url("..."); or @import url('...');
    css_content = re.sub(r'@import\s+url\s*\((["\']).*?\1\)\s*;', '', css_content, flags=re.IGNORECASE|re.DOTALL)
    
    # Fallback for unquoted or other formats if necessary, but careful not to be too greedy
    # css_content = re.sub(r'@import\s+url\s*\(.*?\)\s*;', '', css_content, flags=re.IGNORECASE)
    
    # Remove external URLs (picsum, etc) from background-images
    # This is expanding on the user's error for picsum
    css_content = re.sub(r'url\s*\(\s*["\']?https?://picsum\.photos.*?["\']?\s*\)', 'none', css_content, flags=re.IGNORECASE)
    # Also generic external images if necessary, but let's stick to picsum for now as requested
    
    # Add imports to HTML head if not already there
    if imports:
        links_html = ""
        for url in imports:
            links_html += f'    <link rel="stylesheet" href="{url}">\n'
        
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"{links_html}</head>")
        else:
            # Prepend to body if head missing (rare)
            html_content = links_html + html_content
            
    return css_content, html_content

def process_directory(root, files):
    html_path = os.path.join(root, "template.html")
    
    # Check for style.css OR styles.css
    css_filename = "style.css"
    if "styles.css" in files:
        css_filename = "styles.css"
    css_path = os.path.join(root, css_filename)
    
    if "template.html" in files:
        with open(html_path, "r") as f:
            html = f.read()
        
        # 1. Sanitize HTML (scripts)
        html = sanitize_html(html)
        
        # 2. Process CSS if exists
        if css_filename in files:
            with open(css_path, "r") as f:
                css = f.read()
            
            css, html = sanitize_css(css, html)
            
            with open(css_path, "w") as f:
                f.write(css.strip())
            
            print(f"Processed CSS in {root} ({css_filename})")
                
        with open(html_path, "w") as f:
            f.write(html.strip())
            
        print(f"Processed HTML in {root}")

def main():
    base_dir = os.path.abspath(TEMPLATES_DIR)
    for root, dirs, files in os.walk(base_dir):
        if "template.html" in files:
            process_directory(root, files)

if __name__ == "__main__":
    main()
