from docx import Document
import os

doc = Document("favoris.docx")

output_dir = "Guides/Images"
os.makedirs(output_dir, exist_ok=True)

count = 1
for shape in doc.inline_shapes:
    image = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
    image_part = doc.part.related_parts[image]
    image_data = image_part.blob

    image_name = f"favoris-etape-{count}.png"
    with open(os.path.join(output_dir, image_name), "wb") as f:
        f.write(image_data)

    print(f"✅ Image enregistrée : {image_name}")
    count += 1
