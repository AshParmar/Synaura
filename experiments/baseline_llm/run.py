import os
import json
from tqdm import tqdm
import dotenv
dotenv.load_dotenv()

# === Runnable experiment entrypoint ===
import sys
from pathlib import Path
from experiments.utils import (
    TEST_IMAGES_DIR,
    ensure_project_root_on_path,
    get_top_prediction,
    list_test_images,
    load_image,
    save_result_json as save_json_utils,
)
ensure_project_root_on_path()
from backend.classify.clasification import classify_image
from backend.vision.gradcam import analyze_region
from backend.utils.preprocess import preprocess_image


# Import ChatGroq and HumanMessage directly
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage



def build_prompt(disease, fuzzy_interval, region):
    return f"Generate a radiology report for the following case:\nDisease: {disease}\nFuzzy Interval: {fuzzy_interval}\nRegion: {region}"

def run_one(image_path: Path, temperature: float, run_id: int) -> dict:
    path = load_image(image_path)
    results = classify_image(path)
    top = get_top_prediction(results)
    disease = top["disease"]
    confidence = float(top["confidence"])
    interval = [float(top["interval"][0]), float(top["interval"][1])]
    image_tensor = preprocess_image(path)
    import cv2
    original_image = cv2.imread(path)
    original_image = cv2.resize(original_image, (224, 224)) / 255.0
    from backend.classify.clasification import model
    _, region = analyze_region(model, image_tensor, original_image, disease)
    prompt = build_prompt(disease, interval, region)
    llm_temp = ChatGroq(
        temperature=temperature,
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    generated_report = llm_temp.invoke([HumanMessage(content=prompt)])
    if hasattr(generated_report, 'content'):
        generated_report = generated_report.content
    return {
        "image": Path(path).name,
        "disease": disease,
        "confidence": confidence,
        "interval": interval,
        "region": region,
        "temperature": temperature,
        "run_id": run_id,
        "generated_report": generated_report,
        "prompt": prompt,
        "retrieved_contexts": None
    }
def main():
    images = list_test_images()
    if not images:
        print(f"No images found in {TEST_IMAGES_DIR}")
        return
    temperatures = [0.2, 0.3, 0.4, 0.5, 0.6]
    all_results = []
    for img in images:
        for run_id, temp in enumerate(temperatures):
            payload = run_one(img, temp, run_id)
            all_results.append(payload)
    out_path = save_json_utils("baseline_llm", Path("all_results.json"), all_results)
    print(f"baseline_llm: all results -> {out_path}")
if __name__ == "__main__":
    main()
