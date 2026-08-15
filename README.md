# Track 1: Customer-Facing AI Agent (Google Gen AI APAC)

A production-ready customer support AI agent powered by **Google Gemini Flash** (`google-genai` SDK) and **Streamlit**, configured for one-command deployment to **Google Cloud Run**.

---

## 🌟 Features
- **Modern Chat Interface**: Powered by Streamlit with custom customer-facing styling and interactive quick inquiry buttons.
- **Next-Gen AI Backend**: Uses Google's official `google-genai` SDK with `gemini-flash-latest` (and multi-model fallback).
- **Multi-Turn Context**: Persistent chat memory maintains full context throughout customer conversations.
- **Enterprise Persona**: Built-in system instructions tailored for customer support, order tracking, returns, shipping, and FAQs.
- **Dual Configuration**: Reads API keys from environment variables, `.env` file, Streamlit secrets, or dynamic UI sidebar input.
- **Cloud Native**: Includes production Dockerfile configured for Google Cloud Run (Port 8080).

---

## 📁 Project Structure

```
.
├── app.py              # Core Streamlit application & Gemini 2.0 integration
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container specification for Cloud Run
├── .env.example        # Environment variable template
├── .dockerignore       # Excluded files during container build
├── .gitignore          # Git exclusion rules
└── README.md           # Documentation & deployment guide
```

---

## 🚀 Local Quickstart

### 1. Clone or Open the Workspace
Ensure you are in the project root directory:
```bash
cd "customer facing ai agent"
```

### 2. Create and Activate a Virtual Environment
```bash
# On Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Edit `.env` and insert your Gemini API Key from [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Test with Docker Locally

```bash
# Build the Docker container
docker build -t customer-agent .

# Run the container locally (passing API key)
docker run -p 8080:8080 -e GEMINI_API_KEY="your_api_key_here" customer-agent
```
Open `http://localhost:8080` in your browser.

---

## ☁️ Deploy to Google Cloud Run

Deploy directly from Google Cloud Shell using source-to-container deployment:

```bash
gcloud run deploy customer-agent \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="<YOUR_GEMINI_API_KEY>"
```

### Deployment Parameters:
- `--source .`: Automatically builds container image using Cloud Build.
- `--region asia-southeast1`: Deploys to Singapore region (APAC).
- `--allow-unauthenticated`: Makes the customer support web portal publicly accessible.
- `--set-env-vars`: Seamlessly injects `GEMINI_API_KEY` into Cloud Run runtime environment.
