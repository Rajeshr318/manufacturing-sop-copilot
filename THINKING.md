\# THINKING.md



\## 1. Understand the User



The intended users are manufacturing employees such as machine operators, maintenance technicians, quality inspectors, and safety personnel.



They frequently need to search multiple PDF manuals and SOP documents to find information about machine maintenance, safety procedures, quality inspections, and troubleshooting.



The goal of this application is to provide a natural-language interface that retrieves relevant information from the available manufacturing documents and presents answers with source document and page references.



The application is designed as an information retrieval assistant, not a replacement for authorized maintenance or safety decisions.



\## 2. User Journey



1\. The user opens the Manufacturing SOP AI Copilot through the Streamlit interface.

2\. The user selects a suitable template, such as Machine Maintenance, Safety \& LOTO, or Quality Inspection.

3\. The user enters a question in natural language.

4\. The backend retrieves relevant document chunks from ChromaDB using semantic similarity.

5\. The retrieved context is passed to the Groq-hosted language model.

6\. The application displays the generated answer and source document references.

7\. The user can open the cited PDF to verify the original information.



The application was also tested on a mobile phone connected through the same Wi-Fi hotspot. The chatbot and PDF source links worked successfully.



\## 3. AI Challenge (Conversation Excerpts and Reflection)



\### Challenge 1: Retrieving maintenance schedules



\*\*Question:\*\* Who is responsible for monthly, quarterly, and yearly TX-200 maintenance?



During testing, the model initially attributed the yearly maintenance responsibility to the Maintenance Technician. The document's maintenance schedule contains multiple rows with different responsibilities.



\*\*Improvement:\*\* I updated the prompt instructions to make the model distinguish the maintenance frequencies and their corresponding responsible roles.



\*\*Reflection:\*\* I learned that retrieving relevant text is not enough. Document structure, especially tables, must also be preserved and interpreted correctly.



\### Challenge 2: Missing relevant retrieval results



\*\*Question:\*\* Who performs monthly spindle runout checks and quarterly maintenance activities?



Initially, the retrieval results did not contain enough relevant information to answer the combined question.



\*\*Improvement:\*\* I increased the retrieval top\_k value from 3 to 6 and tested the result again.



\*\*Reflection:\*\* Retrieval configuration affects answer quality. Retrieving more relevant context can help with questions involving multiple maintenance activities.



\### Challenge 3: Unsupported questions



\*\*Question:\*\* What is the monthly electricity consumption of the factory?



\*\*Observed result:\*\* The chatbot responded that it could not find sufficient information in the available manufacturing documents.



\*\*Reflection:\*\* A RAG application should not invent information when the knowledge base does not contain the answer.



\### Challenge 4: Source verification



The chatbot provides source document names and page references. I also implemented citation ID validation so that the application does not display citations that were not included in the retrieved context.



I learned that citation validation helps prevent unsupported source references, although it does not independently prove that every generated statement is supported by the cited passage.



\## 4. The Improvement I Added, and Why I Chose It



I implemented the following improvements:



\- \*\*Document revision handling:\*\* QC-SOP-014 Revision 04 is treated as active, while Revision 03 is excluded from normal retrieval to prevent outdated instructions from being used.

\- \*\*Retrieval improvement:\*\* Increased top\_k to 6 after testing questions that required information from multiple maintenance schedule entries.

\- \*\*Prompt improvement:\*\* Added clearer instructions for interpreting maintenance frequencies and responsible roles.

\- \*\*No-answer handling:\*\* The application returns a no-answer response when sufficient relevant information is unavailable or the generated response cannot pass the expected validation.

\- \*\*Citation validation:\*\* Citation IDs are checked against the retrieved document chunks.

\- \*\*Mobile accessibility:\*\* Updated API and document URLs to allow access from a phone connected to the same local network.



I selected these improvements based on issues observed during actual testing rather than adding features without a clear requirement.



\## 5. Final Reflection



My biggest challenge was ensuring that the chatbot returned accurate answers from manufacturing documents, especially when the documents contained tables, different revision numbers, and safety-related instructions.



I handled this by testing different questions, examining retrieved chunks, adjusting retrieval settings, improving prompt instructions, and checking the chatbot's responses against the original PDFs.



This project helped me understand the practical workflow of a Retrieval-Augmented Generation application, including PDF ingestion, text chunking, embeddings, vector search, LLM-based answer generation, citation handling, and unsupported-question behavior.



I also learned that a successful RAG application requires more than connecting an LLM to a vector database. Document quality, retrieval relevance, prompt design, and evaluation are equally important.



In the future, I would improve table-aware document extraction, retrieval evaluation, citation-to-claim verification, and configurable deployment settings. I would also add more automated tests using a larger set of manufacturing questions.



The application is intended to assist users in finding documented information. Critical maintenance and safety actions must always be verified against the approved procedures and authorized personnel.

