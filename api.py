from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from PIL import Image, ImageChops, ImageEnhance, ExifTags
import exifread

app = FastAPI()

class FolderRequest(BaseModel):
    folder_path: str

def extract_pil_metadata(image_path: str) -> Dict[str, Any]:
    metadata = {}
    try:
        image = Image.open(image_path)
        info = image._getexif()
        if info:
            for tag, value in info.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                metadata[str(tag_name)] = str(value)
        else:
            metadata['Info'] = "No EXIF metadata found using PIL."
    except Exception as e:
        metadata['Error'] = f"Error reading image with PIL: {e}"
    return metadata

def extract_exifread_metadata(image_path: str) -> Dict[str, Any]:
    metadata = {}
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            if tags:
                for tag in tags.keys():
                    metadata[str(tag)] = str(tags[tag])
            else:
                metadata['Info'] = "No EXIF metadata found using exifread."
    except Exception as e:
        metadata['Error'] = f"Error reading image with exifread: {e}"
    return metadata

def perform_ela(image_path: str, ela_output_folder="ela_results", quality=90) -> str:
    try:
        if not os.path.exists(ela_output_folder):
            os.makedirs(ela_output_folder)

        original = Image.open(image_path).convert('RGB')
        temp_filename = os.path.splitext(os.path.basename(image_path))[0] + "_temp.jpg"
        temp_path = os.path.join(ela_output_folder, temp_filename)
        original.save(temp_path, 'JPEG', quality=quality)

        resaved = Image.open(temp_path)
        ela_image = ImageChops.difference(original, resaved)

        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0 / max_diff if max_diff != 0 else 1
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
        ela_filename = os.path.splitext(os.path.basename(image_path))[0] + "_ela.png"
        ela_output_path = os.path.join(ela_output_folder, ela_filename)
        ela_image.save(ela_output_path)

        return ela_output_path
    except Exception as e:
        return f"Error during ELA for {image_path}: {e}"

@app.post("/process-folder")
def process_all_images(request: FolderRequest):
    folder_path = request.folder_path
    supported_formats = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
    results = []

    if not os.path.exists(folder_path):
        return {"error": "Folder not found"}

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            image_path = os.path.join(folder_path, filename)
            pil_metadata = extract_pil_metadata(image_path)
            exif_metadata = extract_exifread_metadata(image_path)
            ela_image_path = perform_ela(image_path)

            results.append({
                "image": filename,
                "metadata_pil": pil_metadata,
                "metadata_exifread": exif_metadata,
                "ela_image_path": ela_image_path
            })

    return {"results": results}
