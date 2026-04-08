import re

with open('original_bloque_2', 'r', encoding='utf-8') as f:
    content = f.read()

# The wrapper div from bloque_1
wrapper_div = '<div style="width: 100%; max-width: 1400px; margin: 0 auto; padding: 100px 48px; font-family: \'Montserrat\', Helvetica, Arial, sans-serif; color: #1a1a1a; box-sizing: border-box; background-color: #ffffff;">'

# Find the body tag
body_match = re.search(r'<body[^>]*>', content)
if body_match:
    body_tag = body_match.group(0)
    # Replace body tag with a plain body, and insert the wrapper div immediately after
    new_body = '<body>\n' + wrapper_div
    content = content.replace(body_tag, new_body)

# Close the wrapper div right before closing body tag
content = content.replace('</body>', '</div>\n</body>')

with open('bloque_2', 'w', encoding='utf-8') as f:
    f.write(content)

print("bloque_2 generated.")
