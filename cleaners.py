import os
from dotenv import load_dotenv
load_dotenv()
import json
from bs4 import BeautifulSoup
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def clean_search_query_response(raw_json_str):
    try:
        data = json.loads(raw_json_str)
        cleaned_docs = []
        for doc in data.get("docs", []):
            cleaned_docs.append({
                "id": doc.get("tid"),
                "title": doc.get("title"),
                "date": doc.get("publishdate"),
                "court": doc.get("docsource"),
                "author": doc.get("author"),
                "summary": doc.get("headline", "").replace("\n", " ").replace("\\n", " ").strip()
            })
        return cleaned_docs
    except Exception as e:
        return {"error": str(e)}

def clean_search_document_response(raw_json_str):
    try:
        data = json.loads(raw_json_str)

        # Parse and clean the HTML
        raw_html = data.get("doc", "")
        soup = BeautifulSoup(raw_html, "html.parser")
        full_text = soup.get_text(separator="\n", strip=True)

        # Generate summary from full_text using Gemini
        prompt = (
            "Summarize this Indian court judgment/law in detail:\n\n"
            + full_text
        )

        response = model.generate_content(prompt)
        summary = response.text.strip()

        return {
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e)}