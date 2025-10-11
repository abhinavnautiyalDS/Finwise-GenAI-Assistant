# Task 1: Chatbot with Memory

## Objective: Build a conversational chatbot that retains context across interactions.

## Tools Used : LLM: Gemini Pro via Google AI Studio API
Framework: LangChain (Python)
Memory: ConversationBufferMemory or ConversationSummaryBufferMemory

## Explanation : 

1. First i store collected Api in colab Secrets
2. then i define my llm
3. i define a ConversationSummaryBufferMemory
4. then i include my llm in memory to make my model memory present
5. finally i use gradio in order to visualise my chatbox
