"""
Streamlit app to test Mac Foundation Model for Typos, Grammar, and Rephrase.
Requires: macOS 26+, Apple Intelligence, pip install streamlit apple-foundation-models
Run: streamlit run app_streamlit.py
"""

import streamlit as st

st.set_page_config(page_title="Mac Foundation Model – Proofread & Rephrase", layout="centered")

st.title("Mac Foundation Model – Proofread & Rephrase")
st.caption("Correct typos, fix grammar, or rephrase for clarity using Apple Intelligence on device.")

# Task type
task = st.radio(
    "**Task**",
    options=["Typos", "Grammar", "Rephrase"],
    horizontal=True,
    help="Typos: fix spelling. Grammar: fix grammar and punctuation. Rephrase: improve clarity and conciseness.",
)

# Map to loader category
category_map = {"Typos": "Typo", "Grammar": "Grammar", "Rephrase": "Rephrasing"}
category = category_map[task]

# Input text
default_typo = "I recieved your email yesterday. The weather is beautifull today."
default_grammar = "I like coffee he prefers tea. If I was in your position I would consider it."
default_rephrase = "It is important to note that we are currently in the process of reviewing the documents."
defaults = {"Typos": default_typo, "Grammar": default_grammar, "Rephrase": default_rephrase}

input_text = st.text_area(
    "**Input text**",
    value=defaults[task],
    height=180,
    placeholder="Type or paste text here...",
    help="Max length is truncated to 12,000 characters to stay within the model's context window.",
)

if not input_text.strip():
    st.info("Enter some text above, then click **Correct**.")
    st.stop()

# Load model on first use
@st.cache_resource
def get_model():
    try:
        from mac_foundation_model_loader import MacFoundationModel, mac_foundation_model_available
        if not mac_foundation_model_available():
            return None, "Mac Foundation Model not available. Requires macOS 26+ and Apple Intelligence."
        return MacFoundationModel(), None
    except Exception as e:
        return None, str(e)

model, load_error = get_model()
if load_error:
    st.error(load_error)
    st.stop()

# Correct button
if st.button("Correct", type="primary"):
    with st.spinner("Running Mac Foundation Model…"):
        try:
            corrected = model.correct(input_text.strip(), category=category)
        except Exception as e:
            st.error(f"Error: {e}")
            corrected = None
    if corrected is not None:
        st.success("Done")
        st.subheader("Corrected text")
        st.text_area("Output", value=corrected, height=200, key="output", disabled=True)
        st.download_button("Download result", corrected, file_name="corrected.txt", mime="text/plain")
