import os
import torch
from backend.utils.preprocess import preprocess_image
from torchvision import models
from torch import nn

model = models.densenet121(weights=None)
model.features.conv0 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
num_ftrs = model.classifier.in_features
model.classifier = nn.Linear(num_ftrs, 5)

CLASSES = ["Cardiomegaly", "Edema", "Consolidation", "Pneumonia", "Pleural Effusion"]
_checkpoint_dir = os.path.dirname(os.path.abspath(__file__))
checkpoint_path = os.path.join(_checkpoint_dir, "densenet121_fuzzy_uselftrained_best.pth")
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")


def _download_weights_from_gcs(dest_path: str) -> bool:
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        print("[classifier] Warning: GCS_BUCKET_NAME is not set. Cannot download model weights.")
        return False

    try:
        from google.cloud import storage
        print(f"[classifier] Downloading model weights from gs://{bucket_name}/weights/densenet121_fuzzy_uselftrained_best.pth…")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob("weights/densenet121_fuzzy_uselftrained_best.pth")

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        blob.download_to_filename(dest_path)
        print("[classifier] [OK] Model weights downloaded successfully.")
        return True
    except Exception as e:
        print(f"[classifier] Error downloading weights from GCS: {e}")
        return False


# Attempt to load model weights
if not os.path.exists(checkpoint_path):
    print(f"[classifier] Model weights file not found at {checkpoint_path}. Attempting to download from GCS...")
    _download_weights_from_gcs(checkpoint_path)

try:
    if os.path.exists(checkpoint_path):
        state = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(state["model"] if isinstance(state, dict) and "model" in state else state)
        model.to(device)
        model.eval()
        print("[classifier] [OK] Model loaded successfully with trained weights.")
    else:
        print("[classifier] Warning: Model weights file is not present. Model initialized with random weights.")
except Exception as e:
    print(f"[classifier] Error loading model weights: {e}")

def classify_image(image_path):
    image = preprocess_image(image_path)
    image = image.to(device)
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.sigmoid(outputs)

    threshold = 0.5
    probs = probabilities[0].cpu().numpy()
    predicted = (probs > threshold)

    MAX_DELTA = 0.10
    results = []
    for i, is_pred in enumerate(predicted):
        if is_pred:
            p = probs[i]
            delta = MAX_DELTA * (1.0 - abs(p - 0.5) * 2.0)
            delta = max(0.0, float(delta))
            lower = max(0.0, p - delta)
            upper = min(1.0, p + delta)
            results.append({
                "disease": CLASSES[i],
                "confidence": p,
                "interval": [lower, upper]
            })

    return results

if __name__ == "__main__":
    results = classify_image("view1_frontalcopy.jpg")
    for r in results:
        print(f"Disease: {r['disease']}, Confidence: {r['confidence']:.4f}, Fuzzy interval: {r['interval']}")