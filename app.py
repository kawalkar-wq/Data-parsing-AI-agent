import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import io
import os

# --- Page Config ---
st.set_page_config(page_title="Oracle Agent v2.0", page_icon="📘", layout="centered")

st.title("📘 Oracle Agent v2.0")
st.subheader("AI-Powered Course Design Preparer")
st.markdown("Upload a PDF and AI will generate a full Course Design Document instantly.")

# --- Hardcoded Groq API Key (free, no credit card) ---
api_key = "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"

# --- File Uploader ---
uploaded_file = st.file_uploader("📂 Upload your PDF", type=["pdf"])

if uploaded_file:
    if st.button("✨ Generate Course Design Document", use_container_width=True):

        with st.spinner("Step 1/3 — Cleaning PDF..."):
            try:
                clean_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        h, w = page.height, page.width
                        safe_zone = (0, h * 0.10, w, h * 0.90)
                        cropped = page.within_bbox(safe_zone)
                        text = cropped.extract_text()
                        if text:
                            clean_text += text + "\n\n"

                if not clean_text.strip():
                    st.error("❌ No text found. The PDF may be scanned or image-based.")
                    st.stop()

            except Exception as e:
                st.error(f"❌ PDF reading error: {e}")
                st.stop()

        with st.spinner("Step 2/3 — AI is generating your Course Design..."):
            try:
                client = Groq(api_key=api_key)
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=2048,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""ROLE: Expert Instructional Designer.
TASK: Use the CLEANED TEXT below to design a detailed Course Design Document.

CLEANED TEXT:
{clean_text[:12000]}

OUTPUT FORMAT (follow exactly):
1. Course Title
2. Target Audience
3. Learning Objectives (5 bullet points)
4. Learning Path with 4-5 Modules:
   - For each Module: Module Title, 3 Topics, 1 Hands-on Lab activity
5. Assessment Strategy
6. Recommended Duration"""
                        }
                    ]
                )
                ai_response = chat_completion.choices[0].message.content

            except Exception as e:
                st.error(f"❌ AI error: {e}")
                st.stop()

        with st.spinner("Step 3/3 — Building your Word document..."):
            try:
                doc = Document()
                doc.add_heading('Course Design Document', 0)
                doc.add_heading('Source Content Summary', level=1)
                doc.add_paragraph(clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text)
                doc.add_heading('AI-Generated Course Design', level=1)
                doc.add_paragraph(ai_response)
                docx_buffer = io.BytesIO()
                doc.save(docx_buffer)
                docx_buffer.seek(0)

            except Exception as e:
                st.error(f"❌ Word doc error: {e}")
                st.stop()

        st.success("✅ Done! Your Course Design Document is ready.")
        st.markdown("### 📋 Generated Course Design")
        st.markdown(ai_response)

        original_name = os.path.splitext(uploaded_file.name)[0]
        st.download_button(
            label="📄 Download Word Document",
            data=docx_buffer,
            file_name=f"{original_name}_CourseDesign.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
else:
    st.info("📂 Please upload a PDF to proceed.")
