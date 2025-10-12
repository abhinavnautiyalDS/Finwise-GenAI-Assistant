<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/2b8457dd-9240-4b28-adcb-068390694dbb" />

## **Task 2: AI Agent with External Tool Access**

## **Objective**
Create an autonomous agent that can use external tools to fetch or calculate data (like interest calculators, stock data, or  Websearch , Runnung Python code).

## **Tools Used**
LangGraph ,Gemini , langchain ,Python ,Alpha Vintage


## **Explaination** 

 1. **Storing API Keys Securely in Colab Secrets**
    The first thing I do is store my Google API key and Alpha Vantage API key in Colab’s secret storage.
    The Google API key allows me to connect with the Gemini model, which is Google’s powerful generative AI model used for understanding and generating text (and  even handling multimodal tasks like images or code).
    The Alpha Vantage API key, on the other hand, helps me access real-time and historical stock market data directly from the Alpha Vantage website. This is essential for building finance-related tools that can fetch or analyse stock prices.

By storing them securely in Colab’s secrets, I ensure that my keys aren’t exposed publicly in the notebook code — keeping my credentials private and safe.

2.  **Defining the LLM Model – Gemini 2.0 Flash**
Next, I define my Gemini 2.0 Flash model.
This version of Gemini is designed for speed and efficiency, meaning it responds faster and consumes fewer tokens than Gemini Pro, which makes it perfect for free-tier usage or lightweight applications.

Despite being lightweight, Gemini 2.0 Flash still performs very well for general reasoning, content generation, and even moderate coding or data analysis tasks. It’s a great balance between performance and cost-effectiveness.

3️. **Creating Four Smart Tools for the Agent**
Once my model is set up, I build four tools that allow it to perform different kinds of actions — almost like giving the model “hands” to interact with the world.

Here’s what each tool does:

🧮 Calculator – This tool handles complex mathematical operations, especially those related to finance, such as compound interest, portfolio variance, or risk-return calculations. It ensures numerical accuracy and precision.

🐍 Python REPL – This allows the model to execute Python code dynamically. So whenever a problem involves complex logic, simulations, or data visualisations, the model can simply write and run Python code to solve it.

💹 Stock Price – This tool connects with the Alpha Vantage API to retrieve the current price and historical trends of various stocks. It’s useful for market analysis, investment insights, or comparing stock performance.

🌐 Web Search – This uses the DuckDuckGo search API to browse the web in real-time. The model can look up fresh or trending information — something not present in its training data — and combine that with its reasoning ability for a more up-to-date answer.

By combining these tools, the model can perform multi-step reasoning — like understanding a financial question, retrieving stock data, performing a mathematical calculation, and presenting the answer in a clear, structured format.

4️. **Testing the Model on Different Queries**
Finally, I test the model by asking it different types of questions — from financial calculations and market analysis to general reasoning or code execution tasks.

During testing, I observe how effectively it uses the tools:

If I ask for the current price of a stock, it calls the Stock Price tool.

For complex financial formulas, it uses the Calculator or Python REPL.

For latest economic news, it relies on Web Search.

This step ensures that the model not only understands natural language but also knows when and how to use each tool intelligently — just like a human analyst equipped with different software utilities.




