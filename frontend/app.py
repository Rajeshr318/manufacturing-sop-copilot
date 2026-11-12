
import os
import html
from urllib.parse import quote

import requests
import streamlit as st


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ForgeIQ",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

API_URL = f"{API_BASE_URL}/ask"
HEALTH_URL = f"{API_BASE_URL}/health"
DOCUMENTS_BASE_URL = f"{API_BASE_URL}/documents/"


# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_title" not in st.session_state:
    st.session_state.chat_title = "New Chat"

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =====================================================
# FORGEIQ DESIGN SYSTEM
# DEEP TEAL + MINT
# =====================================================

st.markdown("""
<style>

/* GLOBAL COLOURS */

:root {
    --forge-bg: #0B1F1E;
    --forge-sidebar: #102A28;
    --forge-card: #173936;
    --forge-card-hover: #1F4944;

    --forge-gold: #39C6A5;
    --forge-champagne: #9BE7D1;
    --forge-light-gold: #D5F7EC;

    --forge-text: #F1F8F5;
    --forge-muted: #A9C2BA;
    --forge-border: #2D514B;

    --forge-green: #78D6A8;
}

.stApp {
    background: var(--forge-bg) !important;
    color: var(--forge-text) !important;
}

/* HIDE DEFAULT STREAMLIT ELEMENTS */

#MainMenu,
footer,
header {
    visibility: hidden;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.8rem;
    padding-bottom: 7rem;
}

/* GLOBAL TEXT */

html,
body,
[class*="css"] {
    font-family: "Inter", "Segoe UI", sans-serif;
}

h1, h2, h3, h4, h5, p, label {
    color: var(--forge-text);
}

.stMarkdown,
.stCaption,
[data-testid="stMarkdownContainer"] {
    color: var(--forge-text);
}

.stCaption,
small {
    color: var(--forge-muted) !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #102A28 0%,
        #0D2523 55%,
        #0B1F1E 100%
    ) !important;

    border-right: 1px solid var(--forge-border);
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--forge-text);
}

/* BRANDING */

.brand {
    padding: 12px 5px 25px 5px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--forge-border);
}

.brand-icon {
    width: 56px;
    height: 56px;
    border-radius: 15px;

    background: linear-gradient(
        135deg,
        #9BE7D1,
        #39C6A5 65%,
        #218F78
    );

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 30px;
    margin-bottom: 13px;

    box-shadow: 0 5px 18px rgba(57, 198, 165, 0.20);
}

.brand-name {
    font-size: 28px;
    font-weight: 800;
    color: #F1F8F5;
    letter-spacing: -1.2px;
}

.brand-name span {
    color: var(--forge-champagne);
}

.brand-subtitle {
    font-size: 12px;
    color: var(--forge-muted);
    margin-top: 6px;
    letter-spacing: 0.3px;
}

/* SIDEBAR NAVIGATION */

section[data-testid="stSidebar"] .stButton > button {
    background: #173936 !important;
    color: #F1F8F5 !important;
    border: 1px solid #2D514B !important;
    border-radius: 10px !important;
    min-height: 43px;
    text-align: left;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #1F4944 !important;
    border-color: var(--forge-champagne) !important;
    color: #FFFFFF !important;
}

.system-card {
    background: #173936;
    border: 1px solid var(--forge-border);
    border-radius: 12px;
    padding: 14px;
    margin-top: 25px;
}

.system-online {
    color: var(--forge-green);
    font-size: 13px;
    font-weight: 700;
}

.muted {
    color: var(--forge-muted);
    font-size: 12px;
}

/* MAIN HEADING */

.main-heading {
    font-size: 38px;
    font-weight: 800;
    color: var(--forge-text);
    letter-spacing: -1.2px;
    margin-top: 15px;
    margin-bottom: 10px;
}

.main-heading span {
    background: linear-gradient(
        90deg,
        #D5F7EC,
        #9BE7D1,
        #39C6A5
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.main-description {
    color: var(--forge-muted);
    font-size: 15px;
    line-height: 1.8;
}

/* HERO SECTION */

.hero {
    background:
        radial-gradient(
            ellipse at 12% 85%,
            rgba(57, 198, 165, 0.16),
            transparent 42%
        ),
        radial-gradient(
            ellipse at 90% 5%,
            rgba(155, 231, 209, 0.10),
            transparent 38%
        ),
        linear-gradient(
            120deg,
            #173936,
            #102A28 55%,
            #1A403B
        );

    border: 1px solid #397568;
    border-radius: 20px;
    padding: 36px 32px;
    min-height: 250px;
    margin-top: 20px;

    position: relative;
    overflow: hidden;

    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.25);
}

.hero-label {
    color: var(--forge-champagne);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2.5px;
    margin-bottom: 10px;
}

.hero-icon {
    font-size: 43px;
    margin-bottom: 10px;
}

/* SUGGESTIONS */

.suggestion-label {
    color: var(--forge-champagne);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 30px;
    margin-bottom: 14px;
}

/* BUTTONS */

.stButton > button {
    background: #173936 !important;
    color: #F1F8F5 !important;

    border: 1px solid #2D514B !important;
    border-radius: 11px !important;

    min-height: 48px;
    font-weight: 600;

    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #1F4944 !important;
    border-color: var(--forge-champagne) !important;
    color: #FFFFFF !important;

    box-shadow: 0 4px 14px rgba(57, 198, 165, 0.16);
}

.stButton > button:focus:not(:active) {
    border-color: var(--forge-champagne) !important;
    box-shadow: 0 0 0 2px rgba(155, 231, 209, 0.20) !important;
}

/* PRIMARY BUTTONS */

.stButton > button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #9BE7D1,
        #39C6A5
    ) !important;

    color: #0B1F1E !important;
    border: 1px solid #D5F7EC !important;
}

/* CHAT INPUT */

[data-testid="stChatInput"] {
    background: #173936 !important;
    border: 1px solid #397568 !important;
    border-radius: 16px !important;

    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.20);
}

[data-testid="stChatInput"]:focus-within {
    border: 1px solid var(--forge-champagne) !important;
    box-shadow: 0 0 0 1px var(--forge-champagne) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--forge-text) !important;
    caret-color: var(--forge-champagne) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--forge-muted) !important;
}

/* CHAT INPUT SUBMIT ICON */

[data-testid="stChatInput"] button {
    background: #39C6A5 !important;
    color: #0B1F1E !important;
    border-radius: 9px !important;
}

[data-testid="stChatInput"] button:hover {
    background: #9BE7D1 !important;
}

/* CHAT MESSAGES */

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding-top: 12px;
    padding-bottom: 12px;
}

[data-testid="stChatMessageContent"] {
    color: var(--forge-text) !important;
    line-height: 1.85;
}

[data-testid="stChatMessageContent"] p {
    color: var(--forge-text) !important;
}

/* USER MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {
    background: #173936 !important;
    border: 1px solid #2D514B !important;
    border-radius: 14px;
    padding: 12px;
}

/* ASSISTANT MESSAGE */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {
    background: #102A28 !important;
    border: 1px solid #294B45 !important;
    border-radius: 14px;
    padding: 12px;
}

/* SOURCE DOCUMENT EXPANDERS */

[data-testid="stExpander"] {
    background: #173936 !important;
    border: 1px solid #2D514B !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: var(--forge-champagne) !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--forge-light-gold) !important;
}

[data-testid="stExpander"] p {
    color: var(--forge-text) !important;
}

/* FEATURE SECTION */

.feature-heading {
    text-align: center;
    color: var(--forge-champagne);
    font-size: 18px;
    font-style: italic;
    margin-top: 58px;
    margin-bottom: 26px;
    letter-spacing: 0.3px;
}

.feature-card {
    text-align: center;
    padding: 18px 8px;

    background: #173936;
    border: 1px solid #2D514B;
    border-radius: 13px;

    min-height: 100px;
    transition: all 0.2s ease;
}

.feature-card:hover {
    background: #1F4944;
    border-color: #397568;
}

.feature-icon {
    font-size: 27px;
    margin-bottom: 9px;
}

.feature-title {
    color: #F1F8F5;
    font-size: 13px;
    font-weight: 600;
}

/* DIVIDERS AND LINKS */

hr {
    border-color: var(--forge-border) !important;
}

a {
    color: var(--forge-champagne) !important;
    text-decoration: none !important;
}

a:hover {
    color: var(--forge-light-gold) !important;
    text-decoration: underline !important;
}

/* INPUTS AND SELECT BOXES */

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #173936 !important;
    color: var(--forge-text) !important;
    border-color: var(--forge-border) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #173936 !important;
    color: var(--forge-text) !important;
}

/* SPINNERS */

.stSpinner > div {
    border-top-color: var(--forge-champagne) !important;
}

/* MOBILE RESPONSIVENESS */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-heading {
        font-size: 29px;
    }

    .hero {
        padding: 25px 20px;
        min-height: auto;
    }

    .hero-icon {
        font-size: 35px;
    }

    .feature-heading {
        margin-top: 35px;
    }
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def start_new_chat():
    st.session_state.messages = []
    st.session_state.chat_title = "New Chat"
    st.session_state.chat_started = False
    st.session_state.pending_prompt = None


def get_source_details(source):

    if isinstance(source, dict):

        filename = (
            source.get("source")
            or source.get("file_path")
            or source.get("filename")
            or source.get("file_name")
            or source.get("document")
            or source.get("path")
        )

        page = source.get(
            "page",
            source.get("page_number", None)
        )

    else:
        filename = str(source)
        page = None

    if filename:
        filename = os.path.basename(
            str(filename).replace("\\", "/")
        )

    return filename, page


# =====================================================
# BACKEND REQUEST
# =====================================================

def ask_backend(question):

    try:

        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return (
            result.get("answer", "No answer returned."),
            result.get("sources", []),
            result.get("status", "no_answer")
        )

    except requests.Timeout:

        return (
            "The request timed out. Please try again.",
            [],
            "error"
        )

    except requests.ConnectionError:

        return (
            "Cannot connect to the ForgeIQ backend. Please start the FastAPI server.",
            [],
            "error"
        )

    except requests.HTTPError as error:

        try:
            error_data = error.response.json()

            detail = error_data.get(
                "detail",
                "The backend request failed."
            )

        except (ValueError, AttributeError):

            detail = "The backend request failed."

        return (
            str(detail),
            [],
            "error"
        )

    except requests.RequestException:

        return (
            "A network error occurred. Please try again.",
            [],
            "error"
        )

    except ValueError:

        return (
            "Invalid response received from the backend.",
            [],
            "error"
        )


# =====================================================
# QUESTION PROCESSING
# =====================================================

def process_question(question):

    question = question.strip()

    if not question:
        return

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Generate conversation title
    if not st.session_state.chat_started:

        st.session_state.chat_title = (
            question[:45] + ("..." if len(question) > 45 else "")
        )

        st.session_state.chat_started = True

    # Ask backend
    with st.spinner("Searching manufacturing documents..."):

        answer, sources, status = ask_backend(question)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "status": status
    })


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🏭</div>
        <div class="brand-name">Forge<span>IQ</span></div>
        <div class="brand-subtitle">
            Industrial Knowledge Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):

        start_new_chat()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("##### ◈ NAVIGATION")

    st.caption("💬  Current Conversation")
    st.caption("📚  Knowledge Documents")
    st.caption("⚙️  System Information")

    st.divider()

    with st.expander("⚙️ System Status"):

        try:

            health = requests.get(
                HEALTH_URL,
                timeout=3
            )

            if health.ok:
                st.success("Backend Online")
            else:
                st.error("Backend Unavailable")

        except requests.RequestException:

            st.error("Backend Offline")

        st.caption("Powered by RAG + GenAI")

    st.markdown("""
    <div class="system-card">
        <div class="system-online">● System Online</div>
        <div class="muted" style="margin-top:7px;">
            Industrial AI Workspace
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# MAIN HOMEPAGE
# =====================================================

if not st.session_state.messages:

    st.html("""
<div class="hero">
    <div class="hero-icon">🏭</div>

    <div class="hero-label">
        INDUSTRIAL INTELLIGENCE
    </div>

    <div class="main-heading">
        Welcome to <span>ForgeIQ</span>
    </div>

    <div class="main-description">
        Your intelligent manufacturing knowledge assistant.
        <br>
        Ask questions and find information from technical manuals,
        maintenance procedures and safety guidelines.
    </div>
</div>
""")

    st.markdown(
        '<div class="suggestion-label">✦ TRY ASKING</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "Hydraulic pressure range?",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "What is the normal hydraulic pressure range for the TX-200?"
            )

            st.rerun()

    with col2:

        if st.button(
            "Safety precautions?",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "What safety precautions must be followed before performing maintenance?"
            )

            st.rerun()

    with col3:

        if st.button(
            "Quality inspection steps?",
            use_container_width=True
        ):

            st.session_state.pending_prompt = (
                "What happens when a critical defect is identified during incoming inspection?"
            )

            st.rerun()

    st.markdown("""
    <div class="feature-heading">
        Smarter. Safer. More Efficient.
    </div>
    """, unsafe_allow_html=True)

    feature_cols = st.columns(4)

    features = [
        ("🛡️", "Accurate Information"),
        ("⚡", "Instant Answers"),
        ("📄", "Source References"),
        ("🏭", "Manufacturing Focused")
    ]

    for col, (icon, title) in zip(feature_cols, features):

        with col:

            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
            </div>
            """, unsafe_allow_html=True)


# =====================================================
# CHAT HISTORY DISPLAY
# =====================================================

else:

    st.markdown(
        '<div class="main-heading"><span>ForgeIQ</span> Assistant</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Conversation: {html.escape(st.session_state.chat_title)}"
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            # -----------------------------------------
            # USER MESSAGE
            # -----------------------------------------

            if message["role"] == "user":

                st.markdown(message["content"])

            # -----------------------------------------
            # ASSISTANT MESSAGE
            # -----------------------------------------

            else:

                status = message.get(
                    "status",
                    "answered"
                )

                sources = message.get(
                    "sources",
                    []
                )

                # -------------------------------------
                # ANSWER STATUS
                # -------------------------------------

                if status == "error":

                    st.error(message["content"])

                elif status == "no_answer":

                    st.info(message["content"])

                else:

                    st.markdown(message["content"])

                # -------------------------------------
                # SOURCE DOCUMENTS
                # -------------------------------------

                if status == "answered" and sources:

                    with st.expander("📚 View source documents"):

                        for index, source in enumerate(sources, 1):

                            filename, page = get_source_details(source)

                            citation_id = (
                                source.get("citation_id")
                                if isinstance(source, dict)
                                else None
                            )

                            if citation_id:

                                source_label = (
                                    f"**[{html.escape(str(citation_id))}]**"
                                )

                            else:

                                source_label = f"**Source {index}**"

                            if filename and page is not None:

                                try:
                                    page_number = int(page)

                                except (ValueError, TypeError):
                                    page_number = None

                                if page_number and page_number > 0:

                                    pdf_url = (
                                        DOCUMENTS_BASE_URL
                                        + quote(filename)
                                        + f"#page={page_number}"
                                    )

                                    safe_filename = html.escape(filename)

                                    st.markdown(
                                        f"{source_label} · "
                                        f"[{safe_filename} — "
                                        f"Open page {page_number}]"
                                        f"({pdf_url})"
                                    )

                                else:

                                    st.markdown(
                                        f"{source_label} · "
                                        f"{html.escape(filename)}"
                                    )

                            elif filename:

                                st.markdown(
                                    f"{source_label} · "
                                    f"{html.escape(filename)}"
                                )

                            else:

                                st.markdown(
                                    f"{source_label} · "
                                    "Source details unavailable"
                                )


# =====================================================
# CHAT INPUT
# =====================================================

prompt = st.chat_input(
    "Ask anything about your manufacturing documents..."
)

question = st.session_state.pending_prompt

if question:

    st.session_state.pending_prompt = None

elif prompt:

    question = prompt

else:

    question = None


if question:

    process_question(question)
    st.rerun()
