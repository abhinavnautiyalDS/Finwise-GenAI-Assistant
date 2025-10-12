<img width="260" height="260" alt="image" src="https://github.com/user-attachments/assets/703ebf98-9152-4c12-b557-aa8d3d4652e8" />


# Task 8: Workflow Automation with n8n

##  Objective
Automate workflows that react to outputs from previous modules — for example, triggering alerts, emails, Slack messages, or updating a dashboard automatically.



##  Tools Used
- **n8n**
- **Slack**
- **Gmail**
- **Google Spreadsheet**
- **Gemini (LLM)**



##  Working Overview

<p align="center">
  <img width="1585" height="650" alt="Workflow Diagram" src="https://github.com/user-attachments/assets/3736b3de-9a57-4cb8-ac35-076896fd415b" />
</p>



###  1. Webhook (Trigger Point)

When the **Submit** button is clicked in any of the Streamlit apps — **Summariser**, **RAG**, or **SQL-based**,  
the **Webhook** node receives a **POST request**, acting as the **starting point** of the automation workflow.



###  2. Switch (Decision Block)

The **Switch** node determines **which app** triggered the event:
-  **Document Summariser**
-  **RAG QA Processor**
-  **SQL Query Processor**

Based on this, it routes the workflow into one of three logical branches.



##  Branch 1: Document Summariser

- **Node:** JavaScript → Analyze Document (Gemini)
- The summary text is sent to **Gemini Flash 2.0** for **sentiment analysis**.
- It checks whether the generated summary contains **negative sentiment**.

**If Block → Send Message (Slack):**
- If **negative sentiment = true**, a **Slack message** is sent to notify the team.  
- If **false**, no message is sent.

✅ **Matches Condition 1 perfectly**



##  Branch 2: RAG (Retrieval-Augmented Generation)

- **Node:** JavaScript → Append/Update Row (Google Sheets)
- The **question–answer pair** is appended to a **Google Sheet** for logging and tracking.

This helps maintain a **knowledge base of queries and responses**.

✅ **Matches Condition 2 exactly**



##  Branch 3: SQL Query Processor

- **Node:** JavaScript → Validation (Code Block)
- Checks whether the query result shows **client investments > ₹10L**.

**If Block → Send Message (Gmail):**
- If **true**, sends a **Gmail notification** (alerting about a high-value client).  
- If **false**, no email is triggered.

✅ **Matches Condition 3 precisely**



###  Summary

| Branch | Function | Trigger | Action |
|:-------|:----------|:---------|:--------|
|  Summariser | Sentiment Check | Webhook (POST) | Slack Notification |
|  RAG QA | Knowledge Logging | Webhook (POST) | Append to Google Sheets |
|  SQL Processor | High-Value Alert | Webhook (POST) | Send Gmail Notification |



###  Outcome
This automation ensures:
- Real-time notifications   
- Centralized knowledge storage   
- Intelligent workflow branching  
- Fully automated data-driven alerts 



