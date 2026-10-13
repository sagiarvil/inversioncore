from PIL import Image, ImageOps

img = Image.open("/Users/macair1/.gemini/antigravity/brain/4e066d71-b2f9-4ccb-89df-2f4dbf514039/.user_uploaded/media_1791151138374.png").convert("RGBA")
data = img.getdata()

new_data = []
for item in data:
    if item[0] > 200 and item[1] > 200 and item[2] > 200:
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append((255 - item[0], 255 - item[1], 255 - item[2], item[3]))

img.putdata(new_data)
img.save("/Users/macair1/projects/inversioncore/public/logo.png", "PNG")
