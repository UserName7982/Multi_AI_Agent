import base64
from io import BytesIO
from ..dataIngestionPipelines.Images_Ingestion import search_images_from_pdf,get_image
from PIL import Image

def retrive_pil_images(query: str, k: int = 2):
    images = search_images_from_pdf(query, k)
    pil_images = get_image(images)
    return pil_images

def encode_image_to_base64(Images: Image.Image):
    buffered = BytesIO()
    Images.save(buffered, format="jpeg")
    img_str=base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def convert_images_to_base64(query: str, k: int = 2):
    # Array List 
    pil_images = retrive_pil_images(query, k)
    encoded_images = []
    for img in pil_images:
        encode_str=encode_image_to_base64(img["pil_image"])
        encoded_images.append({
            "image_id": img["image_id"],
            "doc": img["doc"],
            "page": img["page_no"],
            "encoded_image_base64": encode_str
        })
    return encoded_images
