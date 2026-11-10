
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="Manufacturing SOP AI Copilot",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Manufacturing SOP AI Copilot")

st.write(
    "Ask questions about manufacturing procedures, "
    "quality inspection, safety, and machine maintenance."
)

st.divider()

question = st.text_area(
    "Enter your question",
    placeholder="Example: What is the recommended coolant concentration for TX-200?",
    height=100
)

if st.button("Get Answer", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching SOP documents and generating answer..."):

            try:
                response = requests.post(
                    API_URL,
                    json={"question": question},
                    timeout=120
                )

                response.raise_for_status()
                result = response.json()

                st.subheader("Answer")
                st.markdown(result["answer"])

                st.divider()

                st.subheader("Source Documents")

                sources = result.get("sources", [])

                if sources:
                    for source in sources:
                        st.markdown(
                            f"- **{source['filename']}** "
                            f"(Page {source['page']})"
                        )
                else:
                    st.info("No source documents returned.")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. "
                    "Please start the backend server."
                )

            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")

            except requests.exceptions.RequestException as error:
                st.error(f"API request failed: {error}")

            except Exception as error:
                st.error(f"Unexpected error: {error}")

st.divider()

st.caption(
    "Manufacturing SOP AI Copilot | "
    "Powered by FastAPI, LangChain, ChromaDB and Groq"
)
