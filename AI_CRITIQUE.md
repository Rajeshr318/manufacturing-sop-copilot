\# AI Critique – Manufacturing SOP AI Copilot



\## 1. Overview



I evaluated my Manufacturing SOP AI Copilot to understand how accurately it retrieves information from manufacturing documents and generates answers using Retrieval-Augmented Generation (RAG).



I tested the application with five assignment questions and five additional custom questions to evaluate answer accuracy, document references, and its ability to handle unsupported questions.



\## 2. What Worked Well?



\- The chatbot successfully retrieves relevant information from the manufacturing PDF documents.

\- It provides answers in simple natural language.

\- It displays the source document name and page number.

\- It correctly identifies important machine parameters such as coolant concentration and hydraulic pressure.

\- It provides information about maintenance schedules and safety procedures.

\- It successfully handles questions when the required information is not available in the documents.



\## 3. Issues Identified During Testing



During testing, I identified the following issues:



\*\*Incomplete answers:\*\*

Initially, some answers did not include all the required details. For example, the BH-220 outer diameter answer did not include the nominal dimension, measuring instrument, and defect classification.



\*\*Irrelevant citations:\*\*

The chatbot sometimes displayed additional retrieved documents that did not directly support the generated answer.



\*\*Unsupported questions:\*\*

The chatbot initially displayed an unrelated source document when answering a question about factory electricity consumption, even though the information was unavailable.



\*\*Retrieval limitations:\*\*

Some questions required more specific document passages to provide complete answers.



\## 4. Improvements Implemented



To address these issues, I made the following improvements:



\- Implemented a relevance threshold in the retrieval process to filter less relevant document chunks.

\- Excluded superseded document revisions from normal retrieval.

\- Updated the RAG prompt to restrict answers to the supplied document context.

\- Introduced structured JSON responses containing answers and citation IDs.

\- Added citation validation to ensure that returned source IDs belong to the retrieved passages.

\- Implemented safe no-answer handling when the model cannot provide a supported answer.



\## 5. Testing Results



I tested the chatbot using ten questions.



| Test area | Result |

|---|---|

| Coolant concentration | Correct |

| AL-104 alarm | Correct |

| LOTO lock removal | Correct |

| BH-220 dimensions and tolerance | Correct after improvement |

| Spindle runout schedule | Correct after improvement |

| Maintenance safety procedure | Mostly correct |

| Hydraulic pressure | Correct |

| Critical defect handling | Correct after improvement |

| Chuck mounting bolt torque | Correct |

| Unsupported electricity question | Correct refusal |



\## 6. Remaining Limitations



\- Citation validation confirms that a citation belongs to a retrieved passage, but does not independently verify that every cited passage supports the complete answer.

\- Retrieval accuracy depends on document quality, chunking, and the relevance threshold.

\- The system currently works with the provided manufacturing documents and does not automatically retrieve updated SOP revisions.

\- The chatbot should not replace official documents or authorized safety and maintenance decisions.



\## 7. Conclusion



This evaluation helped me understand the importance of retrieval accuracy, answer completeness, citation validation, and safe handling of unsupported questions in a RAG application.



By testing the application and improving its retrieval and citation logic, I made the chatbot more reliable for answering questions based on manufacturing SOP documents. I also identified areas that can be improved further in future versions.

