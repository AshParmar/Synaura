# backend/vision/gradcam.py

import cv2
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image



def generate_gradcam(model, image_tensor, original_image):

    # Use DenseNet's last normalization layer for GradCAM
    target_layers = [model.features.norm5]

    cam = GradCAM(model=model, target_layers=target_layers)
    grayscale_cam = cam(input_tensor=image_tensor)[0]

    # Normalize original_image to [0,1] and convert to RGB
    if original_image.max() > 1.0:
        original_image = original_image / 255.0
    if original_image.shape[-1] == 1:
        original_image = np.repeat(original_image, 3, axis=-1)

    # Clip values to [0,1] for safety
    original_image = np.clip(original_image, 0, 1)

    # Smooth the Grad-CAM mask for less pixelation
    grayscale_cam = cv2.GaussianBlur(grayscale_cam, (7, 7), 0)
    grayscale_cam = np.clip(grayscale_cam, 0, 1)

    # Overlay Grad-CAM mask with original image
    heatmap = show_cam_on_image(original_image, grayscale_cam, use_rgb=True)

    return heatmap, grayscale_cam

def detect_region(cam, disease):

    disease = disease.lower()

    h, w = cam.shape

    # -------------------------
    # Disease-specific overrides
    # -------------------------
    if disease == "cardiomegaly":
        return "cardiac region (enlarged heart silhouette)"

    if disease == "pleural effusion":
        return "pleural space (lung base)"

    if disease == "edema":
        return "bilateral lung fields (diffuse opacities)"

    if disease == "normal":
        return "no abnormal region detected"

    # -------------------------
    # Default lung-based logic
    # -------------------------
    left_score = cam[:, :w//2].mean()
    right_score = cam[:, w//2:].mean()

    side = "left lung" if left_score > right_score else "right lung"

    upper_score = cam[:h//2, :].mean()
    lower_score = cam[h//2:, :].mean()

    zone = "upper zone" if upper_score > lower_score else "lower zone"

    return f"{side} {zone}"


def analyze_region(model, image_tensor, original_image, disease):

    # Generate GradCAM
    heatmap, cam_mask = generate_gradcam(
        model,
        image_tensor,
        original_image
    )

    # Detect region using disease-aware logic
    region = detect_region(cam_mask, disease)

    return heatmap, region


# Test function for Grad-CAM
if __name__ == "__main__":
    import sys
    import torch
    from torchvision import models, transforms
    from torch import nn
    from PIL import Image
    import cv2
    import os

    # Optional: python gradcam.py <disease_label>  (e.g. Cardiomegaly, Edema — match CLASSES)
    disease_label = sys.argv[1] if len(sys.argv) > 1 else "Cardiomegaly"

    # Load model
    model = models.densenet121(pretrained=False)
    model.features.conv0 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Linear(num_ftrs, 5)
    checkpoint_path = os.path.join(os.path.dirname(__file__), '../classify/densenet121_fuzzy_uselftrained_best.pth')
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    state = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state["model"] if isinstance(state, dict) and "model" in state else state)
    model.to(device)
    model.eval()

    # Load and preprocess image
    image_path = os.path.join(os.path.dirname(__file__), '../classify/view1_frontalcopy.jpg')
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_resized = cv2.resize(img, (224, 224))
    pil_img = Image.fromarray(img_resized)
    tf = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ])
    image_tensor = tf(pil_img).unsqueeze(0).to(device)

    # Prepare original image for visualization
    original_image = img_resized.astype(np.float32)
    original_image = np.expand_dims(original_image, axis=-1)

    heatmap, region = analyze_region(model, image_tensor, original_image, disease_label)
    print("Disease (for region logic):", disease_label)
    print("Detected region:", region)

    # Save heatmap
    cv2.imwrite("gradcam_heatmap.jpg", cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR))
    print("Grad-CAM heatmap saved as gradcam_heatmap.jpg")