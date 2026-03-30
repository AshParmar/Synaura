"""
Script to print and remove test images for which the classifier returns no predictions.
"""
from experiments.utils import list_test_images, load_image
from backend.classify.clasification import classify_image
from pathlib import Path
import os

skipped = []
for img in list_test_images():
    path = load_image(img)
    results = classify_image(path)
    if not results:
        print(f"[REMOVE] {img}")
        skipped.append(img)
        # Remove the file
        try:
            os.remove(img)
            print(f"Removed: {img}")
        except Exception as e:
            print(f"Failed to remove {img}: {e}")
if not skipped:
    print("All test images returned predictions.")
