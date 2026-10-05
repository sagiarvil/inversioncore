from PIL import Image, ImageOps

# Load image and convert to grayscale
img = Image.open("/Users/macair1/.gemini/antigravity/brain/4e066d71-b2f9-4ccb-89df-2f4dbf514039/.user_uploaded/media_1791151138374.png").convert("L")

# The original is dark on white. By inverting it, we get light on dark.
# The white parts (255) will be fully opaque, the black parts (0) fully transparent.
alpha_mask = ImageOps.invert(img)

# Create a new image filled with pure white
result = Image.new("RGBA", img.size, (255, 255, 255, 255))

# Apply the inverted grayscale as the alpha channel
result.putalpha(alpha_mask)

# Save
result.save("/Users/macair1/projects/inversioncore/public/logo.png", "PNG")
