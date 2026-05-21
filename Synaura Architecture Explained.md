# Synaura — Cloud Deployment Architecture (Final)

> Every file explained. Every decision justified. Updated to reflect the actual final stack.

---

## Final Stack Decision Log

| Decision | What we chose | Why |
|---|---|---|
| Vector DB | **FAISS + GCS** (not Pinecone) | Same corpus, zero cost, no extra account |
| Auth | **Clerk v7** | Hosted UI, works with Next.js App Router |
| Frontend hosting | **Vercel** | Zero-config Next.js deployment |
| Backend hosting | **Google Cloud Run** | Serverless, auto-scaling, Docker-native |
| File storage | **Google Cloud Storage** | Stateless containers need external storage |
| Database | **MongoDB Atlas** | Flexible schema for AI report data |
| Monitoring | **Sentry** | Error tracking + performance in production |

---

## The Big Picture

```mermaid
flowchart TD
    USER[End User]
    NEXT[Next.js Frontend on Vercel]
    CLERK[Clerk Auth Gateway]
    CR[Google Cloud Run FastAPI Backend]
    GCS[Google Cloud Storage Bucket]
    FAISS[FAISS Search Index]
    MONGO[MongoDB Atlas Database]
    SENTRY[Sentry Monitoring]
    GH[GitHub Repository]
    GHA[GitHub Actions CI/CD]
    DOCK[Dockerfile]
    GCR[Google Container Registry]

    USER -->|visits| NEXT
    NEXT -->|unauthenticated| CLERK
    CLERK -->|redirects back| NEXT
    NEXT -->|POST /analyze_xray with x-user-id| CR
    CR -->|uploads scan| GCS
    CR -->|searches vectors| FAISS
    CR -->|saves report| MONGO
    CR -->|reports errors| SENTRY
    GH -->|git push main| GHA
    GHA -->|builds| DOCK
    DOCK -->|pushes image| GCR
    GCR -->|deploys to| CR
```

---

## Layer 1 — Docker (Containerization)

> **Goal**: Package the FastAPI app into a portable container so it runs identically on your laptop and on Google Cloud Run.

### `docker/Dockerfile`

```dockerfile
FROM python:3.11-slim          # ← Tiny Linux base image with Python

RUN apt-get install libgl1 ... # ← OpenCV needs these C libraries at runtime

COPY requirements.txt ./
RUN pip install torch ...      # ← CPU-only torch (keeps image size down)
RUN pip install -r requirements.txt

COPY . .                       # ← Copy your source code into the image
RUN pip install -e .           # ← Install your local backend package

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Think of it like**: a recipe card. Anyone following this recipe gets the exact same kitchen every time.

### `docker/docker-compose.yml`

```yaml
services:
  backend:
    build: { dockerfile: docker/Dockerfile }
    env_file: ../.env           # ← Load API keys from .env
    ports: ["8000:8000"]        # ← Your machine port → container port
    volumes: [..:/app]          # ← Mount source for hot-reload (dev only)
```

### `.dockerignore`

```
.git/              # ← Don't send git history (wastes space)
frontend/          # ← Backend image doesn't need frontend
.env               # ← NEVER bake secrets into an image
experiments/       # ← Heavy test data not needed at runtime
cloud/service-account-key.json   # ← GCP credentials — never in image
```

---

## Layer 2 — Environment Variables

> **Goal**: One file documents every secret needed. Never commit real values.

### `.env.example` (full, final)

```bash
# LLM
GROQ_API_KEY=your_key

# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster0.xxx.mongodb.net/synaura

# Google Cloud
GCP_PROJECT_ID=synaura-prod-123456
GCS_BUCKET_NAME=synaura-uploads
GCS_FAISS_BUCKET=synaura-uploads     # same bucket — FAISS index lives here
GOOGLE_APPLICATION_CREDENTIALS=./cloud/service-account-key.json
NEXT_PUBLIC_BACKEND_URL=https://synaura-backend-xxxx-uc.a.run.app

# Clerk (Auth)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx

# Sentry
SENTRY_DSN=https://xxx@o0.ingest.sentry.io/0
```

> [!NOTE]
> Pinecone keys are **not needed** — we use FAISS + GCS instead.

---

## Layer 3 — Database (MongoDB Atlas)

> **Goal**: Persist every AI-generated report so users can see their history.

```
database/
├── mongo_client.py   ← "Open the door to MongoDB"
├── models.py         ← "What shape is the data?"
└── crud.py           ← "What can you DO with the data?"
```

### `mongo_client.py` — Connection

```python
def get_db():
    # ONE connection, reused forever (lazy singleton)
    _client = MongoClient(os.getenv("MONGODB_URI"))
    return _client["synaura"]
```

### `models.py` — Schema

```python
class ScanReportDocument(TypedDict):
    user_id: str          # Clerk user ID
    disease: str          # AI finding
    confidence: float
    region: str           # Lung region
    report: str           # Full markdown report
    heatmap_base64: str   # GradCAM image
    gcs_url: str          # GCS path to original scan
    created_at: datetime
```

### `crud.py` — Operations

```python
save_scan_report(doc)              # Insert → returns report_id
get_report_by_id(report_id)        # Fetch one report
get_reports_for_user(user_id, 20)  # Fetch user's last 20 reports
delete_report(report_id)           # Delete
upsert_user(user_id, email, name)  # Create or update user on login
```

### How `main.py` uses it

```python
# After AI analysis:
doc = new_scan_report(user_id=x_user_id, disease=disease, ...)
report_id = save_scan_report(doc)   # saved to MongoDB Atlas

# New endpoint:
GET /reports/{user_id}  →  get_reports_for_user(user_id)
```

---

## Layer 4 — Vector Search (FAISS + GCS)

> **Decision: No Pinecone.** FAISS is faster, free, and sufficient for a fixed medical corpus.
> The only problem with FAISS on Cloud Run is that containers are stateless — the index lives on disk and disappears on restart. Solution: store the index in GCS and download it on startup.

```
backend/data/faiss_index/    ← your local index (built by build_index.py)
        ↓  (one-time upload)
GCS: gs://synaura-uploads/faiss_index/faiss_index.zip
        ↓  (every Cloud Run cold start)
backend/rag/faiss_loader.py  ← downloads + loads into memory
        ↓
backend/rag/retriever.py     ← hybrid retrieval (vector + BM25)
```

### `backend/rag/faiss_loader.py` — The Production Loader

```python
@lru_cache(maxsize=1)   # load once, cache forever in this container
def load_faiss_db():
    if os.getenv("GCS_FAISS_BUCKET"):
        # Production: download from GCS
        _download_from_gcs(bucket_name, tmp_dir)
        return FAISS.load_local(tmp_dir + "/faiss_index", embeddings)
    else:
        # Local dev: load from disk directly (unchanged from before)
        return FAISS.load_local("backend/data/faiss_index", embeddings)
```

### `cloud/upload_faiss_to_gcs.py` — One-Time Upload

```bash
# Run this once after building/rebuilding the FAISS index:
python -m cloud.upload_faiss_to_gcs

# Output: ✅ Done. gs://synaura-uploads/faiss_index/faiss_index.zip
```

> [!NOTE]
> The `vector_store/` folder (Pinecone files) still exists in the repo as optional scale-up infrastructure but is **not used** in the current deployment.

---

## Layer 5 — Google Cloud Storage (GCS)

> **GCS serves two purposes**:
> 1. Store uploaded X-ray scans permanently (containers can't keep files)
> 2. Store the FAISS index so Cloud Run can download it on cold start

### `cloud/gcs_client.py`

```python
def upload_scan(local_path) -> str:
    blob_name = f"scans/{uuid.uuid4()}.png"
    bucket.blob(blob_name).upload_from_filename(local_path)
    return f"gs://synaura-uploads/{blob_name}"   # returned and saved to MongoDB
```

**Same bucket, two folders:**
```
gs://synaura-uploads/
├── scans/          ← uploaded X-rays (one per analysis)
└── faiss_index/    ← faiss_index.zip (downloaded on cold start)
```

---

## Layer 6 — Authentication (Clerk v7)

> **Goal**: Gate the `/demo` page behind a sign-in wall. Pass the user's ID to the backend so reports get saved per-user.

### File Structure

```
frontend/src/
├── middleware.ts                        ← protects /demo route
├── app/
│   ├── layout.tsx                       ← wraps app with <ClerkProvider>
│   ├── sign-in/[[...sign-in]]/page.tsx  ← dark-themed Clerk sign-in UI
│   └── sign-up/[[...sign-up]]/page.tsx  ← dark-themed Clerk sign-up UI
└── components/
    ├── Navbar.tsx                       ← shows Sign In / UserButton
    └── Demo.tsx                         ← sends x-user-id header
```

### `middleware.ts` — Route Protection

```typescript
const isProtectedRoute = createRouteMatcher(["/demo(.*)"]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();   // → redirects to /sign-in if not authenticated
  }
});
```

### `layout.tsx` — ClerkProvider Wrapper

```tsx
export default function RootLayout({ children }) {
  return (
    <ClerkProvider>          // ← makes auth available everywhere
      <html>
        <body>
          <Navbar />
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
```

### `Navbar.tsx` — Auth-Aware (Clerk v7 pattern)

```tsx
// Clerk v7 uses useUser() hook — NOT <SignedIn>/<SignedOut> (those were removed in v7)
const { isSignedIn } = useUser();

{isSignedIn ? (
  <UserButton />          // ← avatar + dropdown (sign out, manage account)
) : (
  <>
    <Link href="/sign-in">Sign In</Link>
    <Link href="/demo">Try Demo →</Link>
  </>
)}
```

> [!WARNING]
> `<SignedIn>`, `<SignedOut>`, `<SignInButton>` were **removed in @clerk/nextjs v7**. Use `useUser().isSignedIn` for conditional rendering in client components instead.

### `Demo.tsx` — Passing User ID to Backend

```tsx
const { userId } = useAuth();   // Clerk user ID

const res = await fetch("/api/analyze_xray", {
  method: "POST",
  body: formData,
  headers: userId ? { "x-user-id": userId } : {},   // ← backend reads this
});
```

### Full Auth Flow

```
User visits /demo
      ↓
middleware.ts: not signed in?
      ↓
Redirect → /sign-in  (Clerk's dark-themed UI)
      ↓
User signs in with email/Google
      ↓
Redirect back → /demo (NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/demo)
      ↓
Demo loads, useAuth() returns userId = "user_2abc..."
      ↓
User uploads X-ray → POST /analyze_xray
      Header: x-user-id: user_2abc...
      ↓
Backend saves report to MongoDB under that userId
      ↓
GET /reports/user_2abc... → returns all their past reports
```

---

## Layer 7 — Cloud Infrastructure Config

### `cloud/cloudbuild.yaml` — Automated Pipeline (3 steps)

```
Step 1: docker build -f docker/Dockerfile -t gcr.io/PROJECT/synaura-backend:sha .
Step 2: docker push gcr.io/PROJECT/synaura-backend
Step 3: gcloud run deploy synaura-backend --image=... --memory=2Gi --max-instances=10
```

Triggered by connecting your GitHub repo to **Cloud Build → Triggers** in GCP console.

### `cloud/cloudrun_deploy.sh` — Manual Deploy

```bash
bash cloud/cloudrun_deploy.sh
# Builds → pushes → deploys in one command
```

---

## Layer 8 — CI/CD (GitHub Actions)

### `.github/workflows/backend.yml`

```
git push main
    ↓
Job 1: ruff lint (backend/, database/, cloud/)
    ↓
Job 2: pytest tests/
    ↓
Job 3: docker build + push to GCR  [main branch only]
    ↓
Job 4: gcloud run deploy            [main branch only]
```

**GitHub Secrets required:**

| Secret | Value |
|---|---|
| `GCP_PROJECT_ID` | your GCP project ID |
| `GCP_SA_KEY` | base64 of service-account-key.json |
| `GROQ_API_KEY` | your key |
| `MONGODB_URI` | Atlas connection string |

### `.github/workflows/frontend.yml`

```
git push (touching /frontend)
    ↓
Job 1: ESLint
    ↓
Job 2: next build (catches TypeScript errors)
```

Frontend auto-deploys to **Vercel** separately (connected via GitHub integration).

---

## Layer 9 — Monitoring (Sentry)

```python
# backend/main.py — only activates if SENTRY_DSN is set
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=...,
        integrations=[FastApiIntegration(), StarletteIntegration()],
        traces_sample_rate=0.2,   # record 20% of requests for perf
    )
```

Captures: unhandled exceptions, slow requests, MongoDB errors, GCS errors.

---

## Layer 10 — The Upgraded `backend/main.py`

```python
load_dotenv()          # ← load .env first, before any import reads env vars
sentry_sdk.init(...)   # ← monitoring (graceful no-op if SENTRY_DSN not set)

app = FastAPI(...)
app.add_middleware(CORSMiddleware, allow_origins=["localhost:3000", "*.vercel.app"])

@app.get("/health")         # ← Cloud Run readiness probe
@app.post("/analyze_xray")  # ← main AI endpoint, now accepts x-user-id header
@app.get("/reports/{user_id}")  # ← fetch past reports for a user
```

Every cloud integration (MongoDB, GCS, Sentry) **gracefully no-ops** if its env var is missing — local dev never breaks.

---

## Complete File → Purpose Map (Final)

| File | Purpose | Activated by |
|---|---|---|
| `docker/Dockerfile` | Build backend image | `docker build` / GitHub Actions |
| `docker/docker-compose.yml` | Run locally | `docker compose up` |
| `.dockerignore` | Keep image small + secrets out | Automatically by Docker |
| `.env.example` | Document all secrets | You copy → `.env` |
| `database/mongo_client.py` | MongoDB singleton | `MONGODB_URI` |
| `database/models.py` | Document schemas | Imported by crud.py |
| `database/crud.py` | CRUD operations | Imported by main.py |
| `backend/rag/faiss_loader.py` | Production FAISS loader | `GCS_FAISS_BUCKET` env var |
| `backend/rag/retriever.py` | Hybrid retrieval | Called during analysis |
| `cloud/upload_faiss_to_gcs.py` | Upload FAISS index | Run once manually |
| `cloud/gcs_client.py` | Upload scans to GCS | `GCS_BUCKET_NAME` |
| `cloud/cloudbuild.yaml` | GCP build pipeline | Cloud Build trigger |
| `cloud/cloudrun_deploy.sh` | Manual deploy | `bash cloud/cloudrun_deploy.sh` |
| `src/middleware.ts` | Protect /demo route | Every request |
| `src/app/layout.tsx` | ClerkProvider wrapper | App startup |
| `src/app/sign-in/[[...]]/page.tsx` | Dark-themed sign-in | Unauthenticated /demo visit |
| `src/app/sign-up/[[...]]/page.tsx` | Dark-themed sign-up | New user registration |
| `src/components/Navbar.tsx` | Auth-aware navbar | Every page |
| `src/components/Demo.tsx` | Sends userId to backend | Every scan analysis |
| `frontend/next.config.ts` | API proxy + Clerk redirect paths | Build time |
| `.github/workflows/backend.yml` | lint→test→build→deploy | Every `git push main` |
| `.github/workflows/frontend.yml` | lint→build check | Every push touching /frontend |
| `tests/test_health.py` | Smoke tests | CI pipeline |
| `backend/main.py` | Wires everything together | FastAPI startup |

---

## The Complete Deploy Journey

```
1. User visits https://synaura.vercel.app/demo
        ↓
2. middleware.ts: not signed in → redirect to /sign-in
        ↓
3. Clerk sign-in page → user authenticates → redirect to /demo
        ↓
4. Demo page loads
   useAuth() → userId = "user_2xyz..."
        ↓
5. User uploads X-ray → POST https://synaura-backend-xx.a.run.app/analyze_xray
   Header: x-user-id: user_2xyz...
        ↓
6. Cloud Run container (FastAPI):
   - faiss_loader downloads index from GCS (cold start only, cached after)
   - classify → GradCAM → Dual-RAG (FAISS+BM25) → i-MedRAG → report
   - gcs_client uploads X-ray to gs://synaura-uploads/scans/uuid.png
   - crud.save_scan_report() persists to MongoDB
        ↓
7. Returns: { disease, confidence, report, heatmap_base64, report_id }
        ↓
8. Any error → Sentry captures it, you get an alert
        ↓
9. You push a fix → GitHub Actions: lint → test → docker build → Cloud Run deploy
```

---

## What You Need to Do Manually (Physical Steps)

### Step 1 — Create accounts + get keys (~45 min)

**MongoDB Atlas** → [cloud.mongodb.com](https://cloud.mongodb.com)
- Free M0 cluster → Database Access → create user → Network Access → 0.0.0.0/0
- Connect → Drivers → copy URI → paste as `MONGODB_URI` in `.env`

**Google Cloud Platform** → [console.cloud.google.com](https://console.cloud.google.com)
- New project → enable: Cloud Run, Cloud Build, Cloud Storage, Container Registry APIs
- Create GCS bucket: `synaura-uploads`
- IAM → Service Accounts → create `synaura-github-actions` → roles: Cloud Run Admin, Storage Admin, Service Account User → download JSON key → save as `cloud/service-account-key.json`
- Paste `GCP_PROJECT_ID` and `GCS_BUCKET_NAME` in `.env`

**Sentry** → [sentry.io](https://sentry.io)
- New project → FastAPI → copy DSN → paste as `SENTRY_DSN` in `.env`

**Clerk** → [clerk.com](https://clerk.com)
- New application → Email + Google sign-in
- Copy Publishable Key + Secret Key → paste in `frontend/.env.local`

---

### Step 2 — Create `frontend/.env.local` (~2 min)

```bash
# frontend/.env.local  (already in .gitignore)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
```

---

### Step 3 — Upload FAISS index to GCS (~5 min)

```bash
# From project root — run once
python -m cloud.upload_faiss_to_gcs
```

---

### Step 4 — Test with Docker locally (~10 min)

```bash
docker compose -f docker/docker-compose.yml up --build
curl http://localhost:8000/health
# → {"status":"ok","version":"1.0.0"}
```

---

### Step 5 — Deploy backend to Cloud Run (~15 min)

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker
bash cloud/cloudrun_deploy.sh
# → gives you: https://synaura-backend-xxxx-uc.a.run.app
```

---

### Step 6 — Set env vars on Cloud Run (~10 min)

GCP Console → Cloud Run → synaura-backend → Edit & Deploy New Revision → Variables tab:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | your key |
| `MONGODB_URI` | Atlas URI |
| `GCS_BUCKET_NAME` | your bucket |
| `GCS_FAISS_BUCKET` | same bucket |
| `SENTRY_DSN` | your DSN |

---

### Step 7 — Set GitHub Secrets (~10 min)

GitHub repo → Settings → Secrets → Actions:

| Secret | Value |
|---|---|
| `GCP_PROJECT_ID` | project ID |
| `GCP_SA_KEY` | base64 of service-account-key.json |
| `GROQ_API_KEY` | your key |
| `MONGODB_URI` | Atlas URI |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk key (for build) |

**Encode the service account key (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cloud\service-account-key.json")) | clip
```

---

### Step 8 — Deploy frontend to Vercel (~10 min)

[vercel.com](https://vercel.com) → New Project → import GitHub repo:
- Root directory: `frontend`
- Add env vars:
  - `NEXT_PUBLIC_BACKEND_URL` = your Cloud Run URL from Step 5
  - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = your Clerk key
  - `CLERK_SECRET_KEY` = your Clerk secret
  - `SENTRY_DSN` = your DSN

---

### Step 9 — Update CORS + push (~2 min)

In `backend/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-actual-app.vercel.app",   # ← replace with real Vercel URL
],
```
```bash
git add -A && git commit -m "fix: add vercel url to cors" && git push
```
GitHub Actions auto-deploys.

---

### Step 10 — Verify (~5 min)

```bash
# Backend alive?
curl https://your-cloudrun-url.a.run.app/health

# Real scan test
curl -X POST https://your-cloudrun-url.a.run.app/analyze_xray \
  -F "file=@data/test/co_test.jpg" \
  -H "x-user-id: test_user_123"

# Reports saved?
curl https://your-cloudrun-url.a.run.app/reports/test_user_123
```

---

## Total Time

| Step | Time |
|---|---|
| Step 1 — Accounts + keys | ~45 min |
| Step 2 — frontend/.env.local | ~2 min |
| Step 3 — Upload FAISS to GCS | ~5 min |
| Step 4 — Docker local test | ~10 min |
| Step 5 — Deploy to Cloud Run | ~15 min |
| Step 6 — Cloud Run env vars | ~10 min |
| Step 7 — GitHub Secrets | ~10 min |
| Step 8 — Vercel deploy | ~10 min |
| Step 9 — CORS + push | ~2 min |
| Step 10 — Verify | ~5 min |
| **Total** | **~2 hours** |

> [!TIP]
> Start with Step 1 (MongoDB Atlas) first since cluster provisioning takes ~3 minutes. Do the GCP setup while you wait.
