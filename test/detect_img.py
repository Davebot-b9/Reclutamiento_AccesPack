from io import BytesIO
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from PIL import Image
import torch
import clip

app = FastAPI()
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

descriptions = [
    "el paquete en buenas condiciones",
    "etc"
]

class ImageResponse(BaseModel):
    description: str
    probability: float


@app.post("/classify", response_model=ImageResponse)
async def classify_image(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(BytesIO(contents))
    img = preprocess(img).unsqueeze(0).to(device)
    text = clip.tokenize(descriptions).to(device)

    with torch.no_grad():
        image_features = model.encode_image(img)
        text_features = model.encode_text(text)
        logits_per_image, logits_per_text = model(img, text)
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    
    index = probs.argmax()
    return ImageResponse(description=descriptions[index], probability=probs[0][index])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)