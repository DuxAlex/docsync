# DocSync AI

DocSync AI is a web application that analyzes the code of a GitHub repository and automatically generates a README.md, as well as identifying potential bugs. It uses the GitHub API and the Gemini language model to perform these tasks.

## Features

* **Repository Analysis:** Receives the URL of a GitHub repository and analyzes the source code (limited to the first 10 files with relevant extensions: .js, .py, .html, .css, .java, .go, .rb, .php, .ts).
* **README.md Generation:** Generates a README.md based on the analyzed code, providing a general overview of the project.
* **Bug Detection:** Identifies potential bugs in the code, providing information about their severity, type, problem, correction suggestion, and code snippets before and after the correction suggestion.
* **Complexity Analysis:** Analyzes code snippets provided by the user and returns information about overall complexity, bottlenecks, and optimization suggestions.
* **README Commit:** Allows committing the generated README.md directly to the repository (requires authentication).

## Technologies Used

* **Backend:** Python (Flask), requests, google.generativeai, dotenv
* **Frontend:** HTML, CSS, JavaScript, marked.js, particles.js
* **AI:** Google Gemini
* **API:** GitHub API

## Installation

**Requirements:**

* Python 3.7+
* `pip install Flask requests google-generativeai python-dotenv flask-cors`


**Configuration:**

1. Create a `.env` file in the root of the project with the following variables:
    * `GITHUB_TOKEN`: Your GitHub personal access token (with read permissions for the repositories to be analyzed).
    * `GEMINI_API_KEY`: Your Google Gemini API key.

2. Run the application: `python app.py`
