\# Final Reflection – Manufacturing SOP AI Copilot



\## 1. Project Experience



Building the Manufacturing SOP AI Copilot was a valuable learning experience for me. I learned how Generative AI and Retrieval-Augmented Generation (RAG) can be used to solve practical problems in the manufacturing domain.



My main objective was to build an application that could retrieve information from manufacturing PDF documents and answer user questions with supporting document references.



\## 2. What I Learned



During this project, I gained practical experience with:



\- Extracting text and page information from PDF documents using PyMuPDF.

\- Splitting documents into smaller chunks for efficient retrieval.

\- Generating text embeddings using Sentence Transformers.

\- Storing and searching document embeddings using ChromaDB.

\- Building a RAG pipeline using LangChain and Groq.

\- Creating REST APIs using FastAPI.

\- Building an interactive chatbot interface using Streamlit.

\- Managing API credentials using environment variables.

\- Testing answer accuracy, retrieval relevance, and source citations.



\## 3. Challenges I Faced



One of the main challenges was retrieving the most relevant information from manufacturing documents.



Initially, the chatbot sometimes returned incomplete answers or displayed unrelated source references. I also needed to handle superseded document revisions correctly.



Another challenge was ensuring that the chatbot did not generate answers when the required information was unavailable in the documents.



\## 4. How I Improved the Application



I improved the application by introducing a retrieval relevance threshold, excluding superseded document revisions, updating the RAG prompt, and implementing structured responses with citation ID validation.



I tested the application using five assignment questions and five additional custom questions. These tests helped me identify missing answer details and improve the responses for machine specifications, maintenance procedures, and quality inspection requirements.



The unsupported electricity consumption question also helped me verify the application's no-answer behavior.



\## 5. What I Would Improve Next



In future versions, I would like to:



\- Implement hybrid search using semantic and keyword retrieval.

\- Improve citation verification and answer grounding.

\- Add support for more document formats.

\- Introduce automatic document revision management.

\- Add user authentication and role-based access.

\- Improve the interface and deployment process.

\- Evaluate retrieval performance using a larger test dataset.



\## 6. Final Conclusion



This project helped me understand how different components of a Generative AI application work together, from document ingestion and embedding generation to retrieval and answer generation.



I also learned that building a reliable AI application requires more than generating answers. It is important to verify information, provide accurate references, handle unsupported questions, and identify system limitations.



Overall, this project strengthened my practical understanding of Python, RAG, LangChain, ChromaDB, FastAPI, Streamlit, and LLM integration.

