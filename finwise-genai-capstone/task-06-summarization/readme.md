<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/31a3d5ca-72eb-44af-a5d8-0e6b765a0207" />


## **Task 6: Summarization Engine**

### **Objective**
To automatically summarise long financial documents, reports, or meeting transcripts into short, meaningful, and easy-to-read summaries.  
This helps users quickly grasp the key points without going through lengthy content.

### **Tools Used**
- **Gemini Flash 2.0** – Google’s advanced AI model that understands and generates human-like text efficiently.  
- **LangChain** – Used to connect the model, manage prompts, and handle the summarisation workflow.

---

### **Explanation**

1. **Storing API Keys Securely in Colab Secrets**  
   The first and most important step is keeping API keys safe.  
   I stored both the **Google API key** (for Gemini Flash 2.0) in Colab Secrets.  
   The Google API key helps my notebook communicate with Gemini Flash 2.0, which is capable of understanding complex text, reasoning over it, and even interpreting code or multimodal data.  
   Storing them securely ensures no unauthorised access or accidental exposure.

2. **Loading the Document**  
   Next, I load the document using **PyPDF**, a Python library that extracts text from PDF files.  
   This step allows me to convert unstructured PDF data into clean, machine-readable text that the model can process.

3. **Chunking the Document**  
   If the document is very long, it’s split into smaller, manageable pieces (called *chunks*).  
   This step is crucial because AI models have token limits — meaning they can only read a certain amount of text at a time.  
   By chunking the content, I make sure that no part of the document is skipped or cut off.

4. **Defining the Model and Summarisation Prompt**  
   Once the text is ready, I define my **Gemini Flash 2.0 model** through LangChain.  
   I also create a **custom summarisation prompt**, which guides the model on what kind of summary to produce — for instance, concise, bullet-style, or detailed summaries.  
   The parsed text (or its chunks) is then passed to the model, which generates a clear and meaningful summary.

5. **Testing and Refinement**  
   After the initial summaries are generated, I test them on various financial documents and meeting transcripts.  
   This helps me ensure that the summaries are accurate, readable, and maintain the original context.  
   Minor prompt adjustments are made to improve clarity and tone.

---

### **Working**

Here’s how the whole process works in action:

1. The **user uploads a PDF document** into the Streamlit app.  
2. **PyPDF** loads and extracts the text from it.  
3. If the document is too large, the text is **automatically chunked** into smaller parts.  
4. Each chunk is **sent to the Gemini Flash 2.0 model**, which summarises it based on the prompt.  
5. The model then **combines all partial summaries** into one cohesive final summary.  
6. Users can also **adjust the temperature setting** in the Streamlit app — a higher temperature makes the summary more creative and expressive, while a lower one makes it more factual and precise.

---

### **Deployment**

After thorough testing, the summarisation engine was **deployed on Streamlit** for easy public access.  
The web interface allows users to upload their documents, adjust creativity levels, and receive instant summaries in a clean, readable format.

🔗 **App Link:** [https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/](https://finwise-genai-assistant-epjrwcunmwcaaduuriwskv.streamlit.app/)

<img width="1894" height="859" alt="image" src="https://github.com/user-attachments/assets/23eb0465-9dbb-4813-ba88-bc050eff801c" />

