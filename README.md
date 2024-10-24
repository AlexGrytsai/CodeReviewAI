
  
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