from PIL import Image

def make_transparent(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()
    
    newData = []
    # Beyaz ve beyaza cok yakin (threshold > 230) renkleri transparan yap
    for item in datas:
        # item is (R, G, B, A)
        if item[0] > 230 and item[1] > 230 and item[2] > 230:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    
    # Premium gorunum icin biraz kucultup (resize) antialiasing yapabiliriz
    img = img.resize((128, 128), Image.Resampling.LANCZOS)
    img.save(output_path, "PNG")

make_transparent("/Users/macair1/.gemini/antigravity/brain/52dddd4d-8c7a-42a9-936d-af18acecfd23/.user_uploaded/media_1791214257978.png", "/Users/macair1/projects/inversioncore/public/logo.png")
