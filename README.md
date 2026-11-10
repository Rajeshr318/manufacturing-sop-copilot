\# Manufacturing SOP AI Copilot



An AI-powered Manufacturing SOP Copilot built using Retrieval-Augmented Generation (RAG) to help manufacturing employees retrieve information from technical manuals, quality inspection procedures, maintenance documents, and safety instructions.



\## Project Overview



Manufacturing employees often need to search through multiple PDF documents to find specific technical information. This project provides a chatbot interface where users can ask questions in natural language and receive answers based on the available manufacturing documents.



The application retrieves relevant document passages, generates answers using an LLM, and displays supporting document references and page numbers.



\## Key Features



\- PDF document ingestion and text extraction.

\- Text chunking with overlapping passages.

\- Semantic search using Sentence Transformers.

\- Vector storage and retrieval using ChromaDB.

\- Retrieval-Augmented Generation using LangChain and Groq.

\- FastAPI backend for question answering.

\- Streamlit frontend for chatbot interaction.

\- Source document and page references.

\- Relevance filtering for retrieved passages.

\- Exclusion of superseded SOP revisions.

\- No-answer handling for unsupported questions.

\- Citation ID validation.



\## Technology Stack



| Component | Technology |

|---|---|

| Programming Language | Python 3.12 |

| Backend | FastAPI |

| Frontend | Streamlit |

| LLM Provider | Groq |

| LLM Integration | LangChain |

| Embedding Model | all-MiniLM-L6-v2 |

| Vector Database | ChromaDB |

| PDF Processing | PyMuPDF |

| Environment Variables | python-dotenv |



\## Project Structure



```text

manufacturing-sop-copilot/

│

├── backend/

│   ├── \_\_init\_\_.py

│   ├── main.py

│   ├── ingestion.py

│   ├── chunking.py

│   ├── vector\_store.py

│   ├── retrieval.py

│   ├── rag\_pipeline.py

│   └── test\_groq.py

│

├── frontend/

│   └── app.py

│

├── documents/

│   ├── QC-SOP-014\_Rev03\_Incoming\_Material\_Inspection.pdf

│   ├── QC-SOP-014\_Rev04\_Incoming\_Material\_Inspection.pdf

│   ├── SAF-SOP-003\_Lockout\_Tagout\_Procedure.pdf

│   └── MNT-MAN-CNC-02\_TX-200\_Preventive\_Maintenance.pdf

│

├── vectorstore/

├── tests/

├── .env

├── .gitignore

├── requirements.txt

├── USER\_JOURNEY.md

├── AI\_CRITIQUE.md

└── README.md

```



\## Installation and Setup



\### 1. Clone the repository



```bash

git clone <your-github-repository-url>

cd manufacturing-sop-copilot

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows:



```powershell

venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file in the project root:



```env

GROQ\_API\_KEY=your\_groq\_api\_key

GROQ\_MODEL=openai/gpt-oss-20b

```



Replace the placeholder with your own Groq API key. Never upload your actual `.env` file to GitHub.



\### 5. Add manufacturing documents



Place the required manufacturing PDF documents inside the `documents/` folder.



The superseded QC-SOP-014 Rev03 document is retained for revision-handling tests but excluded from normal retrieval.



\### 6. Process documents



Run the document processing modules in order:



```bash

python -m backend.ingestion

python -m backend.chunking

python -m backend.vector\_store

```



These steps extract PDF text, create chunks, generate embeddings, and store active document chunks in ChromaDB.



\## Running the Application



\### Start the FastAPI backend



Open the first terminal:



```bash

python -m uvicorn backend.main:app --reload

```



Backend API:



```text

http://127.0.0.1:8000

```



Swagger API documentation:



```text

http://127.0.0.1:8000/docs

```



\### Start the Streamlit frontend



Open a second terminal:



```bash

streamlit run frontend/app.py

```



The application will open in your browser.



\## Example Questions



1\. What is the recommended coolant concentration for the TX-200 CNC machine?

2\. What does AL-104 indicate, and what action should the operator take?

3\. Who is authorized to remove a personal Lockout/Tagout lock?

4\. What is the BH-220 outer diameter tolerance?

5\. How frequently should spindle runout be checked?



\### Additional Custom Test Questions



1\. What safety steps are required before TX-200 maintenance?

2\. What is the normal hydraulic pressure range for TX-200?

3\. What happens when a critical defect is identified in an incoming material lot?

4\. What is the required torque for chuck mounting bolts?

5\. What is the monthly electricity consumption of the Hosur factory?



The fifth question is intentionally unsupported by the available documents and should trigger the no-answer response.



\## RAG Workflow



1\. \*\*Document ingestion:\*\* Extract text and page metadata from PDF documents.

2\. \*\*Chunking:\*\* Split extracted content into smaller overlapping text chunks.

3\. \*\*Embedding generation:\*\* Convert document chunks into numerical embeddings.

4\. \*\*Vector storage:\*\* Store active document embeddings in ChromaDB.

5\. \*\*Retrieval:\*\* Find relevant passages using semantic similarity.

6\. \*\*Answer generation:\*\* Send the retrieved context and user question to the Groq LLM through LangChain.

7\. \*\*Citation validation:\*\* Validate generated citation IDs against retrieved passages.

8\. \*\*Response:\*\* Display the answer and supporting source references in Streamlit.



\## Testing and Evaluation



The application was tested with five assignment sample questions and five additional custom questions.



Testing covered:



\- Machine operating parameters.

\- Maintenance schedules.

\- Safety procedures.

\- Quality inspection requirements.

\- Document revision handling.

\- Unsupported question handling.

\- Answer completeness and citation accuracy.



The retrieval relevance threshold was initially calibrated using a small set of diagnostic questions and should be validated further with additional test cases.



\## Local Network Deployment



To make the application accessible to other devices on the same Wi-Fi network:



1\. Start the FastAPI server with:



```bash

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

```



2\. Start Streamlit with:



```bash

streamlit run frontend/app.py --server.address 0.0.0.0

```



3\. Find the host computer's local IPv4 address:



```powershell

ipconfig

```



4\. Access the Streamlit application from another device using:



```text

http://YOUR\_LOCAL\_IP:8501

```



The frontend API URL must also be configured to use the host computer's local IP instead of `127.0.0.1` when accessing the backend from another device. Ensure Windows Firewall allows the required local network connections.



\## Limitations



\- Answers depend on the quality and completeness of the uploaded documents.

\- Semantic retrieval may miss relevant passages.

\- Citation ID validation does not independently prove that a cited passage supports every answer detail.

\- The application does not automatically synchronize updated SOP documents.

\- The system is an information retrieval assistant, not a replacement for official SOPs or authorized safety and maintenance decisions.



\## Future Improvements



\- Improve retrieval using hybrid search.

\- Add more robust citation and answer verification.

\- Support additional document formats.

\- Add document revision management.

\- Implement user authentication and access control.

\- Improve the user interface and deployment security.



\## Safety Disclaimer



This application is intended to assist users in finding information from manufacturing documents. Always verify critical instructions against the latest approved SOP and follow authorized safety, quality, and maintenance procedures.



\## Author



Developed as a Generative AI / Retrieval-Augmented Generation project using Python, LangChain, FastAPI, Streamlit, ChromaDB, and Groq.

