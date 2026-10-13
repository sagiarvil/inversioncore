import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix typeEffect string newline
html = html.replace("element.innerHTML += text.charAt(i) === '\\n' ? '<br>' : text.charAt(i);", "element.innerHTML += text.charAt(i) === '\\n' ? '<br>' : text.charAt(i);")
# If it has literal newline:
html = re.sub(r"element\.innerHTML \+= text\.charAt\(i\) === '\n' \? '<br>' : text\.charAt\(i\);", "element.innerHTML += text.charAt(i) === '\\\\n' ? '<br>' : text.charAt(i);", html)


with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("TypeEffect fixed.")
