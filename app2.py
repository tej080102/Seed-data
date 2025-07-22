import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# === CONFIGURATION ===

#from dotenv import load_dotenv
import os

#load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# === PROMPT ===
# prompt = (
#     "You are an expert in plant biology and seedling identification. "
#     "Carefully analyze the uploaded image of a sprouted seed. Based on your extensive visual knowledge of seeds and sprouts, classify it into one of the following 8 categories:\n\n"
#     "1. Alfalfa\n"
#     "2. Broccoli\n"
#     "3. Clover\n"
#     "4. Chick Pea\n"
#     "5. Radish\n"
#     "6. Lentils\n"
#     "7. Green Peas\n"
#     "8. Mung Bean\n\n"
#     "Important Instructions:\n"
#     "- Only reply with one of the above names. No explanations or additional text.\n"
#     "- If the seed is not clearly identifiable, reply with 'Unknown'.\n"
#     "- Use all of your visual understanding of shape, color, size, and sprouting pattern.\n"
#     "- You may search your internal knowledge to distinguish similar looking sprouts like Alfalfa vs Clover or Mung Bean vs Green Peas.\n\n"
#     "Now classify the seed shown in the image."
# )

prompt = (
  "SYSTEM: You are a plant-biology expert specialising in sprouted-seed identification.\n\n"
  "TASK: Examine the user-supplied image and classify the sprout into **exactly one** of these 8 categories:\n"
  "• Alfalfa • Broccoli • Clover • Chick Pea • Radish • Lentils • Green Peas • Mung Bean\n\n"
  "VISUAL CHECKLIST (think silently):\n"
  "1. Seed/coated shape & size\n"
  "2. Cotyledon thickness & colour\n"
  "3. Hypocotyl / root hair density\n"
  "4. Early leaf morphology (e.g., trifoliate vs broad)\n"
  "5. Colour tone differences (e.g., Broccoli’s deep green vs Radish’s reddish tint)\n"
  "6. Any distinguishing textures or markings\n\n"
  "FEW-SHOT REFERENCES (for the model’s internal comparison - do **not** mention these in the answer):\n"
  "• Example A – image of thin white stems with trifoliate leaflets → Clover\n"
  "• Example B – thick pale-green cotyledons with large seed halves → Green Peas\n\n"
  "INTERNAL REASONING: Think through the checklist and compare to the references step-by-step, but **do not reveal** your reasoning.\n\n"
  "OUTPUT FORMAT: Reply with only one of the eight category names **exactly as written**, or reply **Unknown** if unsure. No additional words."
)

# === UI ===
st.set_page_config(page_title="Seed Classifier 🌱", layout="centered")
st.title("🌱 Sprouted Seed Classifier")
st.markdown("Upload an image of a sprouted seed. The AI will classify it into one of 8 seed types.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("🔍 Classify Seed Type"):
        with st.spinner("Analyzing..."):
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()

            # Call OpenAI API
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                        ],
                    }
                ],
                "max_tokens": 20,
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = response.json()

            try:
                output = result["choices"][0]["message"]["content"].strip()
                st.success("🧠 AI Classification Result:")
                st.markdown(f"### 🌾 {output}")
            except Exception as e:
                st.error("❌ Failed to get a valid response.")
                st.json(result)
