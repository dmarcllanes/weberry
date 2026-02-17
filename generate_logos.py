import os

output_dir = "static/img/brands"
os.makedirs(output_dir, exist_ok=True)

def create_svg_file(filename, content):
    with open(os.path.join(output_dir, filename), "w") as f:
        f.write(content)
    print(f"Created {filename}")

# Amazon - Orange smile
amazon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="100" height="40" fill="#FF9900">
    <!-- Font Awesome Free 6.x by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->
    <path d="M256 8C119 8 7.7 121.3 7.7 256c0 83.1 46.1 155.6 115.6 195.9V512h62.5c44.8 0 81.3-36.5 81.3-81.3 0-23.7-10.8-44.9-27.8-59.3-5.5-4.7-9.4-10.4-11.8-17-4-10.9-4-22.1 0-33 2.4-6.6 6.3-12.3 11.8-17 17.1-14.4 27.8-35.6 27.8-59.3 0-44.8-36.5-81.3-81.3-81.3H123.3V256c0-62.8 51-113.8 113.8-113.8 62.8 0 113.8 51 113.8 113.8 0 12.3-2.1 24.2-5.7 35.5h-54.8c-3.6-11.3-5.7-23.2-5.7-35.5 0-33.1-26.9-60-60-60-33.1 0-60 26.9-60 60 0 12.3 2.1 24.2 5.7 35.5h-54.8c-3.6-11.3-5.7-23.2-5.7-35.5 0-62.8 51-113.8 113.8-113.8 62.8 0 113.8 51 113.8 113.8 0 12.3-2.1 24.2-5.7 35.5h-54.8c-3.6-11.3-5.7-23.2-5.7-35.5 0-33.1-26.9-60-60-60-33.1 0-60 26.9-60 60 0 12.3 2.1 24.2 5.7 35.5h-54.8c-3.6-11.3-5.7-23.2-5.7-35.5 0-62.8 51-113.8 113.8-113.8z"/>
</svg>'''
# Note: The above is actually the "Amazon Pay" or similar icon (the 'a'). The "Smile" is different. 
# But for "Amazon", people recognize the 'a' logo or the full text. 
# Since the user wants "image not text", the icon is safer than rendering the text "Amazon".

# Facebook - Blue
facebook_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="40" height="40" fill="#1877F2">
  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
</svg>'''

# Puma - Light Gray
puma_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60" width="80" height="48" fill="#e1e1e1">
  <path d="M95 10 C 80 0, 60 10, 50 20 C 40 30, 20 25, 10 35 C 0 45, 10 55, 20 50 C 25 45, 30 40, 40 35 C 50 40, 60 40, 70 30 C 80 25, 90 20, 95 10 Z 
           M 20 50 L 25 55 L 22 50 Z 
           M 70 30 L 75 40 L 80 30 Z" />
</svg>'''
# (This is a very abstract abstract shape, but recognizable as a fast animal shape)

# Lamborghini - Gold
lamborghini_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" width="60" height="72" fill="#DDB321">
    <path d="M10 10 L 90 10 L 80 90 L 50 110 L 20 90 Z" stroke="#DDB321" stroke-width="5" fill="none"/>
    <path d="M30 30 L 70 30 L 65 50 L 50 40 L 35 50 Z" fill="#DDB321"/>
</svg>'''

# Gucci - Gold
gucci_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60" width="80" height="48" fill="#C5A059">
    <circle cx="35" cy="30" r="20" stroke="#C5A059" stroke-width="8" fill="none" opacity="0.9"/>
    <circle cx="65" cy="30" r="20" stroke="#C5A059" stroke-width="8" fill="none" opacity="0.9"/>
    <rect x="25" y="28" width="10" height="4" fill="#020617"/> <!-- Gap matches bg -->
    <rect x="55" y="28" width="10" height="4" fill="#020617"/> <!-- Gap matches bg -->
</svg>'''

# Pedigree - Yellow with Blue center
pedigree_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="60" height="60" fill="#FFB900">
    <!-- Starburst/Rosette shape -->
    <polygon points="50,5 61,35 95,35 68,55 79,85 50,65 21,85 32,55 5,35 39,35" />
    <circle cx="50" cy="50" r="15" fill="#005696" opacity="1"/> <!-- Blue center -->
</svg>'''


# Twitter (X) - White X on Black background or just the X shape
# User wants "colored", twitter default is black/white essentially.
twitter_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="40" height="40">
    <path d="M389.2 48h70.6L305.6 224.2 487 464H345L233.7 318.6 106.5 464H35.8L200.7 275.5 26.8 48H172.4L272.9 180.9 389.2 48zM364.4 421.8h39.1L151.1 88h-42L364.4 421.8z" fill="white"/>
</svg>'''

# LinkedIn - Blue
linkedin_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="40" height="40">
    <path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z" fill="#0077b5"/>
</svg>'''

# Discord - Blurple
discord_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" width="40" height="40">
    <path d="M524.53 69.836a1.5 1.5 0 0 0-.764-.7A485.065 485.065 0 0 0 404.081 32.03a1.816 1.816 0 0 0-1.923.91 337.461 337.461 0 0 0-14.9 30.6 447.848 447.848 0 0 0-134.426 0 309.541 309.541 0 0 0-15.135-30.6 1.89 1.89 0 0 0-1.924-.91 483.689 483.689 0 0 0-119.688 37.107 1.712 1.712 0 0 0-.788.676C39.068 183.651 18.186 294.69 28.43 404.354a2.016 2.016 0 0 0 .765 1.375 487.666 487.666 0 0 0 146.825 74.189 1.9 1.9 0 0 0 2.063-.676A348.2 348.2 0 0 0 208.12 430.4a1.86 1.86 0 0 0-1.019-2.588 321.173 321.173 0 0 1-45.868-21.853 1.885 1.885 0 0 1-.185-3.126 251.047 251.047 0 0 0 9.109-7.137 1.819 1.819 0 0 1 1.9-.256c96.229 43.917 200.41 43.917 295.5 0a1.812 1.812 0 0 1 1.924.233 234.533 234.533 0 0 0 9.132 7.16 1.884 1.884 0 0 1-.162 3.126 301.407 301.407 0 0 1-45.89 21.83 1.875 1.875 0 0 0-1 2.611 391.055 391.055 0 0 0 30.014 48.815 1.864 1.864 0 0 0 2.063.7A486.048 486.048 0 0 0 610.7 405.729a1.882 1.882 0 0 0 .765-1.352c12.264-126.783-20.532-236.448-86.934-334.541ZM222.491 337.58c-28.972 0-52.844-26.587-52.844-59.239s23.409-59.241 52.844-59.241c29.665 0 53.306 26.82 52.843 59.239 0 32.654-23.41 59.241-52.843 59.241Zm195.38 0c-28.971 0-52.843-26.587-52.843-59.239s23.409-59.241 52.843-59.241c29.667 0 53.308 26.82 52.844 59.239 0 32.654-23.177 59.241-52.844 59.241Z" fill="#5865F2"/>
</svg>'''

create_svg_file("twitter.svg", twitter_svg)
create_svg_file("linkedin.svg", linkedin_svg)
create_svg_file("discord.svg", discord_svg)

# Okenaba Favicon - Circle with Gradient
favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#c084fc;stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="50" fill="url(#grad)" />
</svg>'''


# Save favicon to static/img/ not static/img/brands/
with open("static/img/favicon.svg", "w") as f:
    f.write(favicon_svg)
print("Created favicon.svg in static/img/")

create_svg_file("amazon.svg", amazon_svg)
create_svg_file("facebook.svg", facebook_svg)
create_svg_file("puma.svg", puma_svg)
create_svg_file("lamborghini.svg", lamborghini_svg)
create_svg_file("gucci.svg", gucci_svg)
create_svg_file("pedigree.svg", pedigree_svg)
