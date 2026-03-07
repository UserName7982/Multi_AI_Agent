import base64
from io import BytesIO
from ..dataIngestionPipelines.Images_Ingestion import search_images_from_pdf,get_image
from PIL import Image
from typing import List


def retrive_pil_images(query: str, k: int = 2):
    images = search_images_from_pdf(query, k)
    pil_images = get_image(images)
    return pil_images

def encode_image_to_base64(Images: List[Image.Image]):
    encoded_images = []
    for img in Images:
        buffered = BytesIO()
        img.save(buffered, format="jpeg")
        img_str=base64.b64encode(buffered.getvalue()).decode("utf-8")
        encoded_images.append(img_str)
    return encoded_images

def send_images_as_base64(query: str, k: int = 2):
    pil_images = retrive_pil_images(query, k)
    encoded_images = encode_image_to_base64(list(pil_images))
    return encoded_images

if __name__ == "__main__":
    query = "human photos"
    encoded_images = send_images_as_base64(query, k=2)
    for idx, img_str in enumerate(encoded_images):
        print(f"Encoded Image {idx + 1}: {img_str}...")  # Print the first 100 characters of the base64 string