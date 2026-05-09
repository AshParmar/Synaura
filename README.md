<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Chest_Xray_PA_3-8-2010.png/640px-Chest_Xray_PA_3-8-2010.png" alt="Synaura Logo" width="120" />
  <h1>Synaura AI Radiology Intelligence</h1>
  <p><strong>Next-Generation Explainable AI for Chest X-Ray Analysis</strong></p>

  [![React](https://img.shields.io/badge/React-18.x-blue.svg?style=for-the-badge&logo=react)](https://reactjs.org/)
  [![Next.js](https://img.shields.io/badge/Next.js-15.x-black.svg?style=for-the-badge&logo=next.js)](https://nextjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg?style=for-the-badge&logo=pytorch)](https://pytorch.org/)
  [![Llama 3](https://img.shields.io/badge/Llama_3-Groq_Cloud-10b981.svg?style=for-the-badge)](https://groq.com/)
  [![LangChain](https://img.shields.io/badge/LangChain-RAG-FF9900.svg?style=for-the-badge)](https://langchain.com/)
</div>

<br />

## 🌟 Overview

**Synaura** is an advanced, end-to-end AI radiology intelligence system built to assist clinicians in analyzing Chest X-rays. Unlike traditional "black-box" models that output a single prediction, Synaura focuses entirely on **explainability, uncertainty quantification, and clinical reasoning**. 

By unifying Deep Learning (CNNs), Fuzzy Logic, Computer Vision (GradCAM), and Retrieval-Augmented Generation (RAG) powered by Large Language Models, Synaura delivers highly accurate predictions backed by transparent visual evidence and formal clinical reports.

---

## 🚀 Key Features & Pipeline

Synaura operates on a sophisticated 5-step computational pipeline:

1. **Input Processing (Tensor Normalization)**
   * Chest X-ray images (PNG, JPG, DICOM) are securely uploaded, resized to `224x224`, and normalized into PyTorch tensors for rapid inference.
2. **CNN Classification (DenseNet-121)**
   * A custom-trained deep learning architecture (DenseNet-121) performs multi-class pathology classification (Normal, Pneumonia, Edema, Consolidation, Cardiomegaly).
3. **Fuzzy Inference Confidence**
   * Eliminates overconfident "softmax" scores. Synaura uses fuzzy logic rules to map raw logits into probabilistic **Fuzzy Intervals (e.g., [89.5% - 94.2%])**, quantifying the model's true diagnostic uncertainty.
4. **GradCAM Localization Overlay**
   * Generates a heatmap of model activations, explicitly highlighting the specific lung regions the AI focused on to make its decision, proving visual transparency.
5. **Dual-Retrieval Hybrid RAG (Support & Differential)**
   * Synaura does not just search for the predicted disease. It dynamically spawns two parallel queries:
     * **Support Query**: Searches the medical literature to confirm the primary diagnosis based on the GradCAM region.
     * **Differential Query**: Deliberately searches for alternative diseases that *mimic* the identified imaging patterns, ensuring the LLM considers critical differentials (especially when the fuzzy confidence is < 98%).
   * Both queries search a FAISS + BM25 Hybrid index. The retrieved evidence is passed to a **Groq-powered Llama-3.1-8b** LLM to generate an instant, HIPAA-compliant clinical report.
6. **Direct Medical-Grade PDF Export**
   * Instantly generate and download the final clinical findings (including text and heatmap imagery) as a formalized, beautifully styled A4 PDF document using a custom `jsPDF` engine.

---

## 📁 Folder Structure

```text
Synaura_RAG/
├── backend/                  # FastAPI & Python AI Pipeline
│   ├── main.py               # Application entry point (API definitions)
│   ├── classify/             # DenseNet-121 CNN and Fuzzy Logic module
│   │   └── clasification.py
│   ├── vision/               # Computer Vision modules
│   │   └── gradcam.py        # Heatmap and bounding box generation
│   ├── rag/                  # Retrieval-Augmented Generation logic
│   │   ├── dual_retrieval.py # Spawns Support & Differential queries
│   │   ├── hybrid_retriever.py # FAISS (Dense) + BM25 (Sparse) search
│   │   ├── imedrag.py        # Clinical report structuring
│   │   └── build_index.py    # Vector DB initialization scripts
│   ├── data/                 # FAISS indexes & medical corpus
│   └── evaluation/           # Scripts to evaluate RAG hit-rates
│
├── frontend/                 # Next.js & React UI
│   ├── next.config.ts        # Next.js API proxy to backend
│   ├── src/
│   │   ├── app/              # App router (pages, layout, global css)
│   │   └── components/       # UI Components
│   │       ├── Demo.tsx      # Main workspace and PDF generation logic
│   │       ├── Hero.tsx      # Landing page header
│   │       └── HowItWorks.tsx# Pipeline explanation UI
│   ├── public/               # Static assets
│   └── package.json          
│
├── .env                      # Environment variables (API Keys)
└── README.md                 # You are here!
```

---

## 🛠️ Tech Stack

### Frontend (User Interface)
* **Framework**: Next.js (App Router), React
* **Styling**: Tailwind CSS v4, Framer Motion (Micro-animations)
* **Icons**: Lucide React
* **PDF Engine**: jsPDF (Client-side generation)

### Backend (AI & Logic)
* **Server**: FastAPI, Uvicorn, Python
* **Deep Learning**: PyTorch, torchvision, OpenCV (GradCAM extraction)
* **RAG / NLP**: LangChain, HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector DB**: FAISS (Hybrid with BM25)
* **LLM Engine**: Groq API (Llama-3.1-8b-instant)

---

## 💻 Getting Started

### Prerequisites
* **Node.js** (v18+ recommended)
* **Python** (v3.9+ recommended)
* A **Groq API Key** for the LLM report generation.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/synaura-rag.git
cd synaura-rag
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your environment variables
# Create a .env file in the root directory (c:\Synaura_RAG\.env) and add:
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```
*The backend API will run on `http://localhost:8000`*

### 3. Frontend Setup
```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```
*The frontend interface will be accessible at `http://localhost:3000`*

---

## 📸 Interface Sneak Peek

Synaura features a breathtaking, premium "dark-mode" clinical interface built with Tailwind CSS and animated entirely using Framer Motion. 

- **Landing Page**: Explains the precise technical pipeline (CNN -> Fuzzy -> GradCAM -> Hybrid RAG).
- **Interactive Workspace**: A clean drag-and-drop system to upload scans and instantly view bounding boxes, GradCAM overlays, fuzzy logic intervals, and LLM text side-by-side.
- **Report Exporter**: Click a button to instantly download a professional, high-fidelity A4 white-paper PDF.

---

## 🛡️ License & Disclaimer

**Disclaimer**: Synaura is an experimental AI pipeline designed for educational, research, and demonstration purposes. It is **not** an FDA-approved medical device. It should not be used for actual diagnostic or clinical decision-making without the oversight of a certified radiologist.

Released under the [MIT License](LICENSE).
