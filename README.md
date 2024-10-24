
  
<h1 align="center"> CodeReviewAI </h1>  

**CodeReviewAI** is a backend prototype for an automated Coding Assignment Review Tool built using Python and FastAPI. This tool leverages OpenAI's GPT API for code analysis and the GitHub API for accessing coding assignment repositories, streamlining the process of reviewing coding assignments.

  ## Introduction    
  In this project, the goal is to create a backend service that performs automated code reviews for coding assignments. The tool fetches code from a specified GitHub repository, analyzes it using OpenAI's GPT API, and returns a structured review including found files, comments, ratings, and conclusions.

## Features

-   Automated code reviews using OpenAI's GPT API.
-   Integration with GitHub API for repository access.
-   Input validation and proper error handling.
-   Asynchronous programming for improved performance.
-   Redis caching for enhanced performance.
-   Detailed logging for tracking interactions with APIs.

## Requirements

To run this project, you need:

-   Python 3.12 or higher
-   FastAPI
-   Redis
-   Poetry for package management
-   Access to OpenAI's API and GitHub API (ensure API keys are stored securely).

## Functionality

1.  **GitHub API Integration**: Fetches repository contents and code files.
2.  **OpenAI API Integration**: Analyzes the code and generates a review.
3.  **Error Handling**: Implements proper error handling and logging for API interactions.


  
## Installation
1. **Clone the repository:**  
	 ```sh  
	  git clone https://github.com/AlexGrytsai/CodeReviewAI  
	 cd https://github.com/AlexGrytsai/CodeReviewAI  
	 ```
 2. **Environment Variables:**  
  Ensure you have a `.env` file in the root directory with the following variables:  
	 ```env
	 GITHUB_TOKET=GITHUB_TOKET
	 OPENAI_API_KEY=OPENAI_API_KEY
	 ```     
       
 3. **Build and start the application using Docker:**  
	 ```sh  
	  docker-compose up  
	 ```
 4. **Access the application:**  
  Open your web browser and navigate to [http://localhost:8000/doc/](http://localhost:8000/doc/) or [http://127.0.0.1:8000/doc](http://127.0.0.1:8000/doc/) - here you can read the documentation..  
      To make a request, follow the [link ](http://127.0.0.1:8000/docs#/default/review_review_post), than put a button
"Try it out". After that - fill in the required data for the request and click "Execute".

## What OpenAI thinks about this project
```json
{
  "detail": "Prompt is too long: 57281 tokens. Max tokens: 30000"
}
```
## Test coverage
![tests](https://i.ibb.co/23P2q0J/image.png)

## Possible ways of scaling
**Scaling Related to GitHub and OpenAI Limits**

For a standard account, GitHub offers a limit of 5,000 requests per hour and 
no more than 100 concurrent requests. I see two possible scaling options:

1.  **Upgrade to GitHub Enterprise Cloud**, which provides a limit of 15,000 requests per hour (250 requests per minute). The cost is $21 per user per month. You can add users as needed to increase the hourly request limit by running multiple applications with different tokens.
    
2.  **Create multiple GitHub accounts**, using a token from another account when the limit is reached. This is a more budget-friendly option, but there is a risk of GitHub blocking accounts due to aggressive requests.
    

For handling large repositories with 100+ files that exceed OpenAI’s token limits in a single request, consider first using **text-embedding-3-small** for initial analysis, followed by **gpt-4-turbo**.

To improve performance, you can use a database to store information for each repository owner. Given the data format, it’s better to use a document-oriented database, like MongoDB or Amazon DocumentDB (which has a free version).

Considering the instability of potential loads on the application, I would choose a **serverless architecture**. This allows for more flexible scaling during high loads.

One possible architecture could be to separate the application into two parts: one for fetching data from GitHub and the other for OpenAI. Each application runs in **AWS ECS**, with scaling rules configured, allowing independent scaling as needed. The applications communicate through a message broker, such as **AWS MQ**, which is also set up for scaling.

For caching, you can use **AWS ElastiCache** or free alternatives. It’s also important to consider that load may vary by region, necessitating deployment in different regions and the use of a load balancer to distribute load across clusters.

You must implement limitations on the number of requests an unauthorized user can send, as well as establish restrictions for authorized users (e.g., 5 new requests if the data is not in the cache or database). It’s unlikely that a real user will send more requests (considering OpenAI’s response time). This will optimize performance, reduce costs, and enhance security—since uncontrolled requests to OpenAI can lead to application crashes and denial of service, slow down response times for other users, and significantly increase AWS service expenses.