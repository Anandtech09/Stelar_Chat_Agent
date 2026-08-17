import os
import json
from dotenv import load_dotenv
load_dotenv()
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

prompt = """
Extract all client contact details and interior design requirements from the conversation history into a structured JSON object.
Return ONLY valid JSON matching this schema:
{
  "client_name": string or null,
  "mobile_no": string or null,
  "location": string or null,
  "client_email": string or null,
  "room_type": string or null,
  "style": string or null,
  "room_length": float or null,
  "room_width": float or null,
  "budget": integer or null,
  "site_visit_slot": string or null
}

If a field is unknown, set it to null.
Do not invent or guess any values that were not mentioned.

User Message:
"name is developer, phnone: 0289839393, place kerala, 14x18 living room, 4 lakh budget, next saturday morning visit"
"""

resp = client.models.generate_content(
    model=model_id,
    contents=prompt,
    config={"response_mime_type": "application/json"}
)
print("LLM Extraction Result:")
data = json.loads(resp.text)
for k, v in data.items():
    print(f"  {k}: {v}")
