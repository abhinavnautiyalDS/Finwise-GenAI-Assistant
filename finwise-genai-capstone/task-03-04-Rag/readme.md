<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/691d53a1-4856-4b52-8e59-97df348cfd43" />

---

##  **Task 3: RAG - Part 1 (Basic Document QA)**

###  **Objective**
Build a system that can **answer questions from your own uploaded documents** using a combination of embeddings and generative AI.

---

###  **Tools Used**
- **LangChain** – For building the RAG (Retrieval-Augmented Generation) pipeline.  
- **sentence-transformers/all-MiniLM-L6-v2** – To generate **embeddings** for document chunks.  
- **Gemini Flash 2.0** – For reasoning and generating answers from retrieved content.  

---

###  **Explanation**

#### **1.  Storing API Keys Securely in Colab Secrets**
The first step is to store the **Google API key** and **Hugging Face API key** in Colab’s secret storage.

- The **Google API key** allows communication with **Gemini Flash 2.0**, Google’s advanced generative AI that can understand and reason over text (and even multimodal inputs like code or images).  
- The **Hugging Face API key** is used to access embedding models for converting document text into **vector representations**.

---

#### **2.  Defining the Hugging Face Embedding Model**
I use the **`sentence-transformers/all-MiniLM-L6-v2`** model to generate embeddings.  
- Embeddings are numerical representations of text that capture semantic meaning.  
- These embeddings allow the system to perform **semantic search**, retrieving the most relevant pieces of text based on user queries.

---

#### **3.  PDF Loader**
- This component loads the uploaded PDF document and parses its content into text.  
- It ensures that the text is clean and ready for **chunking and embedding**.

---

#### **4.  Chunking**
- The parsed document is split into **smaller chunks** (to manage context and vector size).  
- Each chunk is then converted into an **embedding vector** using the Hugging Face model.  
- This allows the system to handle **long documents** efficiently.

---

#### **5.  Vector Store (FAISS)**
- I use **FAISS** to store all embedding vectors.  
- FAISS allows **fast similarity search** to retrieve the most relevant chunks based on a user query.  

---

#### **6.  Conversation Memory**
- I use **ConversationBufferMemory** to keep track of the conversation between the user and the chatbot.  
- This ensures the agent remembers previous interactions, improving **contextual responses**.

---

### ⚙️ **Working Flow**

1. **Document Upload** – The user uploads a PDF document.  
2. **Parsing** – PyPDFLoader parses the PDF content into text.  
3. **Chunking & Embedding** – The document is split into smaller chunks, and embeddings are generated for each chunk.  
4. **Vector Store Storage** – Each chunk’s embedding is stored in **FAISS vector store**.  
5. **Query Handling** – When the user asks a question:  
   - The query is converted into an **embedding vector**.  
   - The retriever performs a **semantic search** between the query embedding and document embeddings in FAISS.  
   - The **most relevant document chunks** are retrieved.  
6. **Answer Generation** – The retrieved chunks, along with the user query, are fed into **Gemini Flash 2.0**, which generates the final answer.  

## **Deployment**

Finaly, i Deployed my model in streamlit 
App link : 

