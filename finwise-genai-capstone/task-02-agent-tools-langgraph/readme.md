<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/2b8457dd-9240-4b28-adcb-068390694dbb" />

---

##  **Task 2: AI Agent with External Tool Access**

###  **Objective**
Create an autonomous agent capable of using **external tools** to fetch or calculate data — such as interest calculators, stock data, web search, or executing Python code dynamically.

---

###  **Tools Used**
- **LangGraph**  
- **Gemini (Google Generative AI)**  
- **LangChain**  
- **Python**  
- **Alpha Vantage API**

---

###  **Explanation**

#### **1.  Storing API Keys Securely in Colab Secrets**
The first step is to store the **Google API key** and **Alpha Vantage API key** in Colab’s secret storage.

- The **Google API key** allows communication with the **Gemini model**, Google’s advanced generative AI that understands and generates natural language (and can even handle multimodal inputs such as code and images).  
- The **Alpha Vantage API key** enables retrieval of **real-time and historical stock market data** from the Alpha Vantage platform — crucial for building finance-related tools that analyse stock trends or performance.

By keeping these keys in Colab’s secrets, I ensure they remain **secure and private**, preventing accidental exposure in the notebook code.

---

#### **2.  Defining the LLM Model – Gemini 2.0 Flash**
Next, I define my **Gemini 2.0 Flash** model.

This version of Gemini is designed for **speed and token efficiency**, making it ideal for free-tier usage and lightweight applications.  
While it’s more efficient than **Gemini Pro**, it still provides impressive capabilities in **reasoning, content generation, and data analysis** — achieving a strong balance between **performance and cost**.

---

#### **3.  Creating Four Smart Tools for the Agent**
Once the model is ready, I create **four intelligent tools** that extend its abilities — essentially giving the AI “hands” to interact with external sources and perform specialised actions.

| Tool | Description |
|------|--------------|
|  **Calculator** | Performs complex mathematical and financial computations (e.g. compound interest, portfolio variance, risk-return analysis) with high precision. |
|  **Python REPL** | Executes Python code dynamically, allowing the model to handle advanced logic, simulations, and data visualisations. |
|  **Stock Price** | Fetches current and historical stock data through the **Alpha Vantage API** for financial insights and performance tracking. |
|  **Web Search** | Utilises the **DuckDuckGo Search API** to access real-time information from the web — ensuring the model can reference the latest data or trends. |

By combining these tools, the agent can perform **multi-step reasoning** — for example:  
1. Understand a financial query.  
2. Retrieve relevant stock data.  
3. Perform necessary calculations.  
4. Deliver a clear, data-backed answer.

---

#### **4.  Testing the Model on Different Queries**
Finally, I test the agent by running it on a variety of **real-world queries** — ranging from financial analyses and stock lookups to Python-based calculations and web research.

During testing, I observe how effectively the agent selects and uses its tools:
- For **stock prices**, it automatically calls the *Stock Price* tool.  
- For **financial formulas**, it switches to the *Calculator* or *Python REPL*.  
- For **news or general knowledge**, it uses the *Web Search* function.  


