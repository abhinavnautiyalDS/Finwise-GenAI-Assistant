<img width="265" height="265" alt="image" src="https://github.com/user-attachments/assets/76619d51-2d6e-49f1-9721-442660d32912" />

## **Task 5: SQL - Based QA System**

## **Objective**
Allow users to query structured financial data using natural language.

## **Tools Used**
- SQL Lite  
- LangChain  
- Gemini Flash 2.0  

## **Explanation**

1. **Storing API Keys Securely in Colab Secrets**  
   The first step is to store the Google API key securely in Colab’s secret storage.  
   This API key acts as a bridge between our notebook and Gemini Flash 2.0, Google’s advanced generative AI model.  
   Gemini Flash 2.0 can understand and reason over natural language, and it’s optimised for both speed and cost efficiency, making it ideal for real-time query handling.

2. **Creating and Connecting to the SQLite Database**  
   Next, we create a new SQLite database named **financialdb**.  
   This database contains two tables:  

   - **clients:** client_id, name, age, risk_profile, portfolio_value  
   - **investments:** investment_id, client_id, fund_name, amount_invested, date  

   Around 30 sample rows are inserted into these tables to simulate real financial data for testing.

3. **Defining the Gemini Model**  
   We then define our Gemini Flash 2.0 model using the LangChain wrapper.  
   This step allows us to use Gemini as our language reasoning engine — meaning it can interpret user queries, understand their intent, and generate accurate, context-aware SQL queries automatically.

4. **Creating the SQL Database Toolkit**  
   After setting up the model, we create an **SQL Database Toolkit**.  
   This toolkit acts as a bridge between the database and the language model, allowing the model to access schema information, query structure, and available columns — so it can form correct SQL queries behind the scenes.

5. **Building the SQL Agent**  
   We then use **create_sql_agent()** to integrate the toolkit, database, and Gemini model together.  
   This agent acts as a smart assistant capable of understanding user questions (like “Which client has the highest portfolio value?”) and translating them into valid SQL queries that fetch real results from the database.

6. **Testing the Working**  
   Finally, we test our setup by asking natural language queries.  
   For example, when we ask *“Show all clients with a high-risk profile who invested more than ₹50,000,”* the SQL agent automatically generates and executes the correct SQL command, retrieves the data, and displays it in a clean, human-readable format.

---

## **Working**

Once the setup is complete, the system becomes capable of answering user queries in natural language directly from structured financial data.  
Here’s how it works step-by-step:

### 1. User Interaction  
The process begins when a user types a query in plain English — for example:  
*“Show me the clients who invested more than ₹1,00,000 in mutual funds.”*  
The user doesn’t need to know SQL commands or database structure; they simply ask questions naturally.

### 2. Query Interpretation (Gemini’s Role)  
The Gemini Flash 2.0 model, integrated through LangChain, analyses the user’s query to understand the **intent and context**.  
It determines what information the user is requesting — for example, clients with investments exceeding a certain amount — and identifies the relevant tables or columns.

### 3. SQL Query Generation  
Using its understanding from the previous step, the SQL Agent automatically converts the natural language query into an appropriate SQL statement.  
For example, Gemini might generate:  

### 4. Execution and Retrieval
The generated SQL query is executed on the SQLite (financialdb) database.
The database processes the query and returns relevant results — such as client names, their risk profiles, and investment amounts.

### 5. Response Formatting
Once results are fetched, Gemini reformats them into a clean, easy-to-understand answer.
Instead of showing raw rows, it summarises conversationally — for example:
“There are 5 clients who have invested more than ₹1,00,000. The top investor is Riya Sharma with an investment of ₹2,50,000.”

## **Deployment**
Finaly i deployed app on streamlit 
App link : https://finwise-genai-assistant-akc6rt3yvowr8edklrzhx9.streamlit.app/
<img width="1910" height="862" alt="image" src="https://github.com/user-attachments/assets/dcd8d56d-6a59-4225-b5cf-cd52b9e3097e" />


