from PIL import Image
from torchvision import transforms
transforms=transforms.Compose(
    [transforms.Resize((224, 224)),
     transforms.ToTensor(),
     transforms.Normalize([0.5], [0.5]),]
)
def preprocess_image(image_path):
    import cv2
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pil_image = Image.fromarray(image)
    image = transforms(pil_image)
    image = image.unsqueeze(0)
    return image