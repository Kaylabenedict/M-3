# pip install transformers Pillow torch streamlit into the shell

import os
import streamlit as st
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
from PIL import Image
import torch

st.title("Image Captioning & Q&A App")

# === Step 1: Hugging Face Token (hidden from UI for security) ===
os.environ["HF_TOKEN"] = "st.secrets["HF_TOKEN]"  # Demo token for workshop

# === Step 2: Image Upload ===
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # === Step 3: Load BLIP model and generate caption ===
    with st.spinner("Generating caption..."):
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            output = model.generate(**inputs)
            caption = processor.decode(output[0], skip_special_tokens=True)
    st.markdown(f"**📝 Caption generated by BLIP model:** {caption}")

    # === Step 4: Use QA model to extract ingredients and steps ===
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

    questions = [
        "What are the ingredients?",
        "What are the cooking actions?"
    ]

    st.markdown("### 🔍 Ask questions about the caption:")
    for i, q in enumerate(questions):
        if st.button(q, key=f"q{i}"):
            with st.spinner("Getting answer..."):
                result = qa_pipeline(question=q, context=caption)
            st.success(f"**Q:** {q}\n\n**A:** {result['answer']}")
else:
    st.info("Please upload an image to get started.")
