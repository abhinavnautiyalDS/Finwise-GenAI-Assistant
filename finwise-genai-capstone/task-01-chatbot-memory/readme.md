<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/3e53cc7e-0a0f-4373-bed2-d31e5e495f06" />



# Task 1: Chatbot with Memory

## Objective:
Build a conversational chatbot that retains context across interactions.

## Tools Used : LLM: Gemini Pro via Google AI Studio API
Framework: LangChain (Python)
Memory: ConversationBufferMemory or ConversationSummaryBufferMemory

## Explanation : 

1. 1st I Store  API key in Colab Secrets to keep it secure and hidden from the code.

2. Retrieve it using userdata.get() or os.environ for safe authentication.

3. Define  LLM (Large Language Model) . Gemini , using that API key.

4. The LLM acts as the main brain that generates responses to your prompts.

5. Create a ConversationSummaryBufferMemory to let the bot remember past chats.

6. This memory summarises older messages, keeping the context concise and relevant.

7. Combine your LLM and memory in a ConversationChain for a context-aware chatbot.

8. The chain maintains conversation flow across multiple user inputs.

9. Use Gradio to build an interactive chat interface for real-time user interaction.

10. Launch the app to visualise and talk with your AI model directly in the browser.

## Deployement : 

Finally i deplloyed my app on streamlit 
App link : https://finwise-genai-assistant-puf9qq6dprr9aqtkchgfcm.streamlit.app/

<img width="1903" height="847" alt="image" src="https://github.com/user-attachments/assets/ba75a161-9c49-4514-96f9-3b8df3973d99" />


