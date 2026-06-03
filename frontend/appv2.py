import streamlit as st
import requests

st.title("🪄 Harry Potter Character Recognizer")
uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, width=300)
    if st.button("Identify"):
        with st.spinner("Analyzing..."):
            response = requests.post("http://api:8000/analyze/",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
)
            if response.status_code == 200:
                data = response.json()
                st.success(f"🧙‍♂️ {data['character']} (confidence: {data['confidence']:.2%})")
                st.balloons()
            else:
                st.error("Error during prediction")