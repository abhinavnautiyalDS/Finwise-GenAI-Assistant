# Finwise – End-to-End Financial GenAI Assistant

**Finwise** is a modular, production-style Generative AI system designed to solve real-world financial problems using Large Language Models, retrieval systems, agents, databases, summarization pipelines, and workflow automation.

<img width="970" height="546" alt="image" src="https://github.com/user-attachments/assets/3bd6662d-2522-47ec-b0a4-9843e5c110bf" />


This project goes beyond a simple chatbot and demonstrates how **stateless LLMs can be converted into reliable, controllable, and scalable applications** by adding memory, tools, reasoning, grounding, and orchestration.

---

## Project Architecture Overview

The project is structured into independent but connected tasks, where each task addresses a specific limitation of raw LLMs:

**Task 1:** Conversational memory  
**Task 2:** Agentic reasoning with tools  
**Task 3 & 4:** Retrieval-Augmented Generation (RAG) with memory  
**Task 5:** Natural language to SQL querying  
**Task 6:** Long document summarization  
**Task 7:** Workflow automation using n8n  

Each module can run independently but also integrates seamlessly with others to form a complete GenAI financial assistant.

---

## Task 1: Financial Chatbot with Memory

### Problem Statement

Large Language Models accessed via APIs are **stateless**, meaning they do not remember previous conversations. Without external memory, a chatbot cannot provide context-aware responses.

### What Was Built

A financial chatbot that can **retain conversational context** and respond intelligently based on previous user interactions.

### Key Technologies Used

**Gemini 2.0 Flash** as the language model  
**LangChain Memory**  
**ConversationChain**

### Memory Mechanisms Implemented

**ConversationBufferMemory** stores the entire conversation history and sends it with every new prompt. This ensures perfect context but increases token usage as conversations grow.

**ConversationSummaryBufferMemory** summarizes older conversations while keeping recent messages intact. This significantly reduces token usage while preserving meaning, making it suitable for long-running chats.

### Why This Matters

This task shows how to **simulate memory in a stateless LLM system** and highlights the trade-off between accuracy, cost, and scalability.

---

## Task 2: Agentic Financial Reasoning with Tools

### Problem Statement

LLMs struggle with multi-step reasoning, numerical accuracy, real-time data, and transparency. In finance, hallucinated answers are unacceptable.

### What Was Built

A **ReAct-style financial agent** capable of reasoning, calling external tools, observing results, and producing accurate, traceable outputs.

### Technologies Used

**LangChain** for tool definitions  
**LangGraph** for agent orchestration  
**Gemini** as the reasoning engine  
**Alpha Vantage API** for real-time stock prices  

### How the Agent Works

The agent follows a **Reason → Act → Observe** loop:

The agent first reasons about the user’s intent, then selects the correct tool, executes it, observes the result, and finally generates a grounded response. The user never directly controls tools—the agent decides autonomously.

### Why LangGraph + LangChain

LangChain provides clean abstractions for tools. LangGraph provides **explicit control over reasoning flow**, retries, and stopping logic. Together, they create a transparent and debuggable agent system.

---

## Task 3 & Task 4: Retrieval-Augmented Generation (RAG) with Memory

### Problem Statement

LLMs should answer questions from **user-provided documents**, not from internal training data. Financial documents are long, complex, and frequently updated.

### What Was Built

A conversational document QA system that:
- Understands PDFs
- Retrieves relevant context
- Answers questions accurately
- Handles follow-up queries using memory

### End-to-End Pipeline

The user uploads a document.  
The document is parsed using **PyPDFLoader**.  
The extracted text is split into overlapping chunks.  
Each chunk is converted into embeddings.  
Embeddings are stored in **FAISS**.  
The user query is embedded and matched via semantic search.  
Relevant chunks are retrieved.  
Gemini generates a grounded, context-aware answer.

### Key Enhancements

**RecursiveCharacterTextSplitter** preserves semantic meaning while respecting context limits.

**MultiQueryRetriever** improves recall by generating multiple rephrased versions of the user query.

**ConversationBufferMemory** enables natural follow-up questions.

### Why This Matters

This task eliminates hallucinations by **grounding LLM responses in real documents** and supports reliable financial QA.

---

## Task 5: Natural Language to SQL Querying

### Problem Statement

Users should be able to query structured financial databases using **plain English**, without writing SQL.

### What Was Built

A system that converts natural language questions into **safe SQL queries**, executes them, and returns human-readable answers.

### Database Design

**SQLite** database with two tables:

**clients**  
client_id (primary key), name, age, risk_profile, portfolio_value  

**investments**  
investment_id (primary key), client_id (foreign key), fund_name, amount, date  

### Core Components

**SQLDatabase** for database connection  
**SQLDatabaseToolkit** for safe database operations  
**SQL Agent** for reasoning and query generation  
**Gemini** for intent understanding and response generation  

### Execution Flow

The user asks a question.  
The SQL Agent interprets intent using the LLM.  
A valid SQL query is generated.  
The query is validated and executed on SQLite.  
Results are converted into natural language.

The user never sees SQL, and the model never guesses data.

---

## Task 6: Financial Document Summarization Engine

### Problem Statement

Long financial documents often exceed LLM context limits, making direct summarization impossible.

### What Was Built

A summarization engine that can process **very long documents** while preserving meaning and structure.

### Summarization Strategies Used

**MapReduce**  
Each chunk is summarized independently, then combined into a final summary.

**Refine**  
The summary is progressively refined as new chunks are processed, similar to how humans read long documents.

### Key Technologies

**PyPDFLoader**  
**RecursiveCharacterTextSplitter**  
**LangChain load_summarize_chain**  
**Gemini LLM**

### Evaluation Approach

Since no gold summary exists, evaluation is qualitative:
- Coverage of key points
- Faithfulness to source
- Clarity and conciseness

This mirrors real-world industry practice.

---

## Task 7: Workflow Automation with n8n

### Problem Statement

AI insights are only valuable if they trigger **real-world actions**.

### What Was Built

An automation layer using **n8n** that reacts to GenAI outputs and triggers:
- Slack alerts
- Email notifications
- Google Sheets logging

### How It Works

The GenAI backend sends results to an **n8n webhook**.  
The webhook triggers the workflow.  
Switch nodes route data based on type.  
Actions are executed automatically.

### Role of n8n

n8n handles **orchestration and integration**, not reasoning.  
AI generates intelligence; n8n operationalizes it.

---

## Evaluation Strategy (Industry-Aligned)

Each task was evaluated using appropriate methods:

Memory correctness for chatbots  
Tool selection accuracy for agents  
Precision and recall for RAG  
SQL correctness and grounding  
Faithfulness and coverage for summarization  
End-to-end reliability for automation  

Where automated metrics were not suitable, **human evaluation** was used, which is standard in production GenAI systems.

---

## Key Takeaways

**LLMs are powerful but incomplete on their own.**  
**Memory, tools, retrieval, and orchestration are essential.**  
**Finance requires transparency and grounding.**  
**Production GenAI is system design, not prompt engineering.**

---

## Final Note

Finwise is not a single model or a single library project.  
It is a **full-stack GenAI system built with real-world constraints in mind**.

