from PIL import Image, ImageOps

img = Image.open("/Users/macair1/.gemini/antigravity/brain/4e066d71-b2f9-4ccb-89df-2f4dbf514039/.user_uploaded/media_1791151138374.png").convert("L")
alpha_mask = ImageOps.invert(img)

# Boost the alpha channel by 2.5x to make the logo completely opaque and bright white,
# while preserving the smooth edges (anti-aliasing).
alpha_mask = alpha_mask.point(lambda p: min(255, int(p * 2.5)))

result = Image.new("RGBA", img.size, (255, 255, 255, 255))
result.putalpha(alpha_mask)
result.save("/Users/macair1/projects/inversioncore/public/logo.png", "PNG")
