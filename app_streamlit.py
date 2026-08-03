import os
import sys
import subprocess

# --- OpenCV Headless Fix for Streamlit Cloud ---
# Streamlit Cloud installs both opencv-python (via grad-cam) and opencv-python-headless.
# This causes libGL/libgthread errors. We force uninstall the GUI version if needed.
try:
    import cv2
except ImportError as e:
    if "libgthread" in str(e) or "libGL" in str(e):
        print("🔧 Attempting to fix OpenCV dependencies for Streamlit Cloud...")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python", "opencv-python-headless"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python-headless"])
        print("✅ OpenCV fixed.")
# -----------------------------------------------

import streamlit as st
import os
from PIL import Image
import numpy as np

import sys
# Ensure the src module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.inference import get_inference_engine

st.set_page_config(
    page_title="Diabetic Retinopathy Detection API",
    page_icon="👁️",
    layout="wide"
)

st.title("👁️ Diabetic Retinopathy & Glaucoma Detection AI")
st.markdown("A complete, production-ready AI pipeline designed to assist ophthalmologists in diagnosing **Diabetic Retinopathy (DR)** and screening for **Glaucoma**.")

@st.cache_resource
def load_engine():
    # Lazy load the inference engine to cache it in Streamlit
    return get_inference_engine()

engine = load_engine()

st.sidebar.title("Settings")
enable_xai = st.sidebar.checkbox("Enable Explainable AI (Grad-CAM)", value=True, help="Generates heatmaps highlighting the lesions.")

uploaded_file = st.file_uploader("Choose a fundus image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image / الصورة الأصلية")
        st.image(image, use_container_width=True)
        
    with st.spinner("Analyzing image... / جاري تحليل الصورة..."):
        try:
            if enable_xai:
                result = engine.predict_with_explanation(image)
            else:
                result = engine.predict(image)
            
            with col2:
                st.subheader("Results / النتائج")
                
                # Main Prediction
                pred_label = result.get('predicted_label', '')
                pred_label_ar = result.get('predicted_label_ar', '')
                confidence = result.get('confidence', 0.0) * 100
                
                st.markdown(f"### Prediction: **{pred_label}**")
                st.markdown(f"### التشخيص: **{pred_label_ar}**")
                st.progress(int(confidence), text=f"Confidence: {confidence:.2f}%")
                
                # Severity and Recommendation
                st.info(f"**Severity (الخطورة):** {result.get('severity', '')} / {result.get('severity_ar', '')}")
                st.warning(f"**Recommendation (توصية):** {result.get('recommendation', '')} \n\n {result.get('recommendation_ar', '')}")
                
                # Glaucoma Risk
                cdr = result.get('cdr_value', 0)
                risk = result.get('glaucoma_risk', '')
                risk_ar = result.get('glaucoma_risk_ar', '')
                
                st.markdown("---")
                st.subheader("Glaucoma Screening / فحص الجلوكوما")
                st.write(f"**vCDR (Cup-to-Disc Ratio):** {cdr:.2f}")
                
                if risk == "High Risk":
                    st.error(f"**Glaucoma Risk (خطر الجلوكوما):** {risk} / {risk_ar}")
                else:
                    st.success(f"**Glaucoma Risk (خطر الجلوكوما):** {risk} / {risk_ar}")
            
            # XAI output if available
            if enable_xai and result.get("gradcam_overlay") is not None:
                st.markdown("---")
                st.subheader("Explainable AI (Grad-CAM Heatmap)")
                st.markdown("Heatmap indicating the regions the model focused on to make the decision.")
                
                overlay = result["gradcam_overlay"]
                # Convert overlay back to PIL if it's numpy array
                if isinstance(overlay, np.ndarray):
                    overlay = Image.fromarray(overlay)
                    
                st.image(overlay, use_container_width=True, caption="Grad-CAM Overlay")
                
                if "interpretation" in result:
                    st.write(f"**EN:** {result['interpretation'].get('en', '')}")
                    st.write(f"**AR:** {result['interpretation'].get('ar', '')}")

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
