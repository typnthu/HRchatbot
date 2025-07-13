# HRchatbot

Build a Virtual HR Chatbot with Amazon Bedrock.

## Introduction

This project aims to develop a chatbot that assists with retrieving information about company policies, employee records, and automating the leave request process at NexusTech. The chatbot is built on the Amazon Bedrock platform, leveraging Knowledge Bases to ensure accurate responses, and integrates Streamlit to provide a user-friendly interface.

## Main Objectives

Develop a chatbot capable of:

Advising and answering inquiries about HR policies (leave requests, employee benefits, disciplinary actions, etc.).

Automatically sending email notifications to confirm leave requests.

Querying and updating employees’ leave balance information.

Integrating Amazon Bedrock Knowledge Bases and a Vector Database to improve response accuracy.

Building a text-based interaction interface using Streamlit.

Deploying a serverless architecture on AWS Lambda and related AWS services.

## Technologies Used

Amazon Bedrock: Deploys the Titan Embedding Model and powers the chatbot.

AWS Lambda: Handles business logic and invokes APIs to send emails.

Amazon SES: Sends notification emails.

Amazon DynamoDB: Stores and queries employee records and leave balance data.

Amazon S3: Stores various project-related data, especially API schema definitions used to structure communication between Lambda and Bedrock.

Amazon CloudWatch: Logs events for monitoring and error tracing.

Streamlit: Builds the interactive web user interface.

Python: Primary programming language.

## System diagram

<img width="940" height="615" alt="image" src="https://github.com/user-attachments/assets/34b3e7dc-3d6a-466b-bb38-8cd6ddfdec6e" />

## System Overview

The Streamlit application is deployed on an EC2 instance and provides an interactive web interface. User authentication is enforced via EmployeeID and password.

When a user submits a query through the Streamlit interface, the EC2 server sends the prompt to the Amazon Bedrock Agent, which analyzes the user’s intent and routes the request accordingly:

If the query relates to company policies, the agent performs a retrieval-augmented search using Titan Embedding and queries the OpenSearch Serverless database within the Knowledge Base to generate an accurate response.

If the query concerns employee-specific data or leave requests, the agent triggers an Action Group that calls AWS Lambda functions based on definitions specified in the API schema stored in S3. Lambda functions execute the required operations, such as retrieving or updating employee records or sending notification emails via Amazon SES.

Once the processing is complete and the response is returned, the agent consolidates the results and delivers a clear answer back to the user through the Streamlit interface.

## Deployment Steps

**1. Environment Preparation**

a. Hardware and Platform

Hardware: Ubuntu 22.04 (amd64) virtual machine with 2 CPUs

b. AWS CLI and SDK Environment

AWS CLI v2

Boto3 SDK

c. Language and Libraries

Python 3.9

Key libraries:

  - boto3: AWS service integration

  - streamlit: Web user interface

**2. Amazon S3**

Upload all required resources and content to an S3 bucket for centralized storage.

<img width="873" height="329" alt="image" src="https://github.com/user-attachments/assets/d842c568-d2b4-4fd2-b440-4c18b17c65f6" />

**3. Amazon DynamoDB**

Import two tables (employee_info and leave_request) from S3 to DynamoDB for structured employee data and leave request tracking.

<img width="940" height="185" alt="image" src="https://github.com/user-attachments/assets/690f001c-263a-47ea-94ce-b0ea833f5e6a" />

**4. AWS Lambda**

_Create a Lambda layer with essential libraries:_

  - aws_lambda_powertools: For structured JSON logging, facilitating efficient search in CloudWatch

  - pydantic: For schema declaration and automatic input validation

  - typing-extensions: To ensure compatibility with Pydantic schema definitions

Ensure the layer is built for the Python 3.9 Lambda runtime environment.

<img width="940" height="77" alt="image" src="https://github.com/user-attachments/assets/92344efa-5da4-426f-abc8-e839bcd9c20c" />

_Develop the main Lambda function (chatbot)_

Organized in a structured directory layout for maintainability and clarity.

<img width="940" height="442" alt="image" src="https://github.com/user-attachments/assets/43b8f91d-4ab5-4d06-9568-0ed180ba1df2" />

**5. Amazon SES (Simple Email Service)**

Verify all sender and recipient email addresses required for demonstration and notifications.

<img width="940" height="246" alt="image" src="https://github.com/user-attachments/assets/f66b750f-2c18-4f5c-873b-01820ece41ee" />

**6. Amazon Bedrock Knowledge Base (KNB)**

Create a Knowledge Base using the NexusTechVI.txt file stored in S3 as the data source.

Embedding Model: Titan Text Embeddings v2

Vector Store: Amazon OpenSearch Serverless

**7. Amazon Bedrock Agent chatbot**

<img width="666" height="451" alt="image" src="https://github.com/user-attachments/assets/9c74978a-88a9-43a8-9f21-8b93a7b18e27" />

Model: Nova Premier 1.0

Agent Instruction:

  "_You are an AI assistant specialized in HR-related questions. Your role is to help employees with inquiries about time off, pay, retirement, and other HR topics. You have access to specific actions and tools to retrieve accurate information._

  _You should provide clear, concise, and empathetic responses tailored to employees’ needs. Maintain a professional, courteous, and approachable tone at all times. When appropriate, guide users step by step through HR procedures, policies, or forms, making complex processes easy to understand._

  _If an inquiry cannot be resolved directly, suggest reliable alternative resources, provide helpful links, or escalate the issue to a human HR representative for further assistance. You must respect employee privacy and confidentiality at all times, ensuring that any personal or sensitive information is handled securely and in accordance with company policies and relevant data protection regulations._

  _You are expected to be proactive in anticipating follow-up questions and offering additional context or clarifications to support the employee’s understanding. Whenever possible, confirm that the employee feels their issue has been addressed fully before closing the conversation._"

Link the Knowledge Base to the agent.

Define Action Groups connecting to Lambda functions using corresponding API schemas.

Create versioning and aliases for easy agent management and deployment.

**7. Streamlit Application**

<img width="930" height="237" alt="image" src="https://github.com/user-attachments/assets/8a52adc4-cec8-40a3-ab31-0ab92ec9c6ad" />


