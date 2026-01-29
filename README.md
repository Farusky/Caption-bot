# 📸 CaptionBot Pro: Multimodal AI SaaS

A professional, conversational AI chatbot designed to generate high-engagement social media captions. Powered by **Google Gemini 1.5 Flash**, this app can "see" images and "hear" your instructions to craft the perfect post.



## ✨ Key Features
* Multimodal Analysis: Upload images (JPG/PNG) and get captions based on visual context.
* Conversational Logic: Fine-tune your results! Ask the bot to "make it shorter" or "add more emojis" without re-uploading the image.
* Dynamic Quantity: Request a specific number of captions (e.g., "Give me 5 captions").
* One-Click Copy: Each caption is delivered in its own individual code block with a built-in copy icon.
* Chat History: Manage multiple conversations simultaneously with the sidebar history and delete functionality.
* SaaS UI: A clean, branded interface built with Streamlit and custom CSS.

## 🛠️ Tech Stack
* Language: Python 3.10+
* AI Engine: Google Generative AI (Gemini API)
* Framework: Streamlit
* Image Processing: Pillow (PIL)
* Security: Python-Dotenv & Streamlit Secrets

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone [https://github.com/Farusky/Caption-bot](https://github.com/Farusky/Caption-bot)
cd Caption-bot

```

### 2. Install dependencies

```bash
pip install -r requirements.txt

```

# 3. Set up your API Key

Create a `.env` file in the root directory:

```text
GOOGLE_API_KEY=your_api_key_here

```

# 4. Run the app

```bash
streamlit run app.py

```

#  Security

This project uses environment variables (`.env`) to ensure API keys are never exposed in the source code. When deployed, keys are managed via Streamlit Secrets.

---

Developed by [Faruk Shehu Zangina (Dev Faruk)]

```
