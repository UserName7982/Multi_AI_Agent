import io
import fitz
import torch
from PIL import Image
import open_clip
from ..DB.VectorDataBase import tbl_image

device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess, preprocess_val = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)
tokenizers = open_clip.get_tokenizer("ViT-B-32")
if isinstance(preprocess, tuple):
    preprocess = preprocess[-1]

model = model.to(device)

def embed_image(pil_img: Image.Image):
    image = preprocess(pil_img).unsqueeze(0).to(device) # type: ignore
    with torch.no_grad():
        feats = model.encode_image(image) # type: ignore
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy()[0]

def embed_extract_imaged_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    items = []
    for page_index in range(doc.page_count):
        images = doc[page_index].get_images(full=True)
        for img in images:
            xref = img[0]
            base = doc.extract_image(xref)
            img_bytes = base["image"]
            pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            pil_image.show()  # Display the image for verification
            items.append({
                "image_id": xref,
                "vector": embed_image(pil_image),
                "page": page_index + 1,
                "doc": pdf_path
            })
    return items

def Ingest_images_from_pdf(pdf_path: str):
    items = embed_extract_imaged_from_pdf(pdf_path)
    row=[]
    for item in items:
        row.append({
            "image_id": item["image_id"],
            "vector": item["vector"].astype("float32").tolist(),
            "page": item["page"],
            "doc": item["doc"]
        })
    tbl_image.add(row)

def get_image(images:list[dict]):
    pil_images=[]
    for item in images:
        docs=fitz.open(item["doc"])
        xref=item["image_id"]
        base=docs.extract_image(xref)
        img_bytes=base["image"]
        pil_image=Image.open(io.BytesIO(img_bytes)).convert("RGB")
        pil_images.append({
            "image_id": item["image_id"],
            "doc": item["doc"],
            "page_no": item["page"],
            "pil_image": pil_image
        })
        pil_image.show()  # Display the image for verification
    return pil_images

def embed_query_text(query: str):
    tokens = tokenizers([query]).to(device) 
    with torch.no_grad():
        feats = model.encode_text(tokens) # type: ignore
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().numpy()[0].astype("float32")  # (512,)


def search_images_from_pdf(query: str, k: int = 2):
    qv = embed_query_text(query).tolist()  # LanceDB likes list[float]
    return tbl_image.search(qv).limit(k).to_list()


if __name__ == "__main__":
    # items = embed_extract_imaged_from_pdf(r"C:\Users\Hello\Desktop\16022026fx\docs\dogcat.pdf")
    # print(items)

    results = search_images_from_pdf("QR")
    get_image(results)