# AI Threat Sentinel 🛡️

**AI Threat Sentinel** is a globally-aware cybersecurity intelligence engine that empowers Security Operations (SecOps) teams. By aggregating active Open-Source Intelligence (OSINT) and employing advanced Large Language Models (Gemini), it provides a synthetic, tactical, and immediately actionable daily cybersecurity brief.

## 🧠 Architecture Overview: RAG-Inspired Intelligence
Traditional AI tools often suffer from "hallucinations" (inventing non-existent data). To circumvent this critical flaw in cybersecurity intelligence, this engine utilizes **Retrieval-Augmented Generation (RAG) concepts**.

Instead of asking the LLM about recent threats (which it might not know about or might hallucinate), the architecture intercepts real-time RSS Feeds from top cybersecurity outlets:
- BleepingComputer
- The Hacker News
- Dark Reading

The engine robustly ingests, filters, and standardizes these fresh sources into an active context payload. Only then is the information sent to the Google Gemini model. This ensures the output is **100% grounded in the real-time contextual payload**, resulting in accurate Executive Reports, mapped CVEs, and real-world attack vectors. 

## ✨ Features
- **Automated OSINT Interception:** Scrapes multiple threat intelligence feeds concurrently.
- **RAG-Grounded Analysis:** Guarantees zero hallucinations by grounding the Generative AI strictly within the ingested news parameters.
- **SecOps Executive Dashboard:** A Streamlit-based UI, providing dark-mode tactile views and full source traceability (hyperlinks to original articles included on the sidebar).

## 🚀 Getting Started

Follow these steps to deploy and run the architecture locally.

### 1. Clone the project
```bash
git clone https://github.com/yourusername/threatlens-ai.git
cd threatlens-ai
```

### 2. Environment Setup
We utilize a virtual environment to isolate the project dependencies constraint.
```bash
# Create the virtual environment
python3 -m venv venv

# Activate it (Linux/MacOS)
source venv/bin/activate
# Or on Windows:
# venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. API Key Configuration
This project relies on Google's Gemini LLM. 
1. Duplicate the example environment config file:
```bash
cp .env.example .env
```
2. Open the newly created `.env` file and safely inject your Gemini API string:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
*(Need an API key? Deploy one for free at the [Google AI Studio](https://aistudio.google.com/app/apikey))*

### 4. Run the Engine
To launch the Streamlit frontend with full interactive OSINT tracing:
```bash
streamlit run app.py
```
Your local environment will spin up the SecOps dashboard automatically at `http://localhost:8501`.

## 🛠️ Tech Stack
- **Interface:** Streamlit
- **Intelligence:** `google-genai` (Deploying Gemini 2.5 Flash)
- **Data Gathering:** `feedparser`, `requests`
- **Data Structuring/Config:** `pandas`, `python-dotenv`

---
*Developed as a modernized AI approach to Security Operations.*
