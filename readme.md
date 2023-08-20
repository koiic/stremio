# Stremio


## WORKBOUNCE TAKE HOME TEST
The purpose of this project is to develop a web API that allows users to retrieve a list of movies, rate them by upvoting or downvoting, and view their own rated movies. The application will require authentication to ensure user privacy and security. The project aims to provide an enjoyable and personalized movie rating experience for users.

## Implementation Details

- Implement user authentication to ensure secure access to the application.
- Enable users to view a list of movies from a datastore and the ability to paginate.
- Allow users to rate movies using upvotes and downvotes.
- Enable users to view a personalized list of rated movies.
- Ensure efficient and seamless retrieval from third party API by using CACHE to store the movie data for 24 hours.
- Implement Retry mechanism to handle errors gracefully and report failed requests.
- Implement a logging mechanism to log errors and user activities.


## AI Technology utilized
During the implementation of my take-home assessment, I leveraged AI tools to streamline and enhance my development process. I utilized ChatGPT to quickly gather a general understanding of how to structure and approach the project. This helped me outline the project's key components and design.

Additionally, I integrated GitHub Copilot into my Integrated Development Environment (IDE) to assist with day-to-day application development. Copilot proved valuable by offering code suggestions aligned with my logic and context, reducing the burden of remembering syntax and enabling me to focus on the core functionality.

In summary, my usage of AI tools such as ChatGPT and GitHub Copilot enhanced my efficiency, provided insightful guidance, and improved the quality of my implementation for the take-home assessment project.


## Technologies

- Python 3.8 or later
- FastAPI
- Uvicorn
- Pytest
- sqlmodel
- sqlite3

## Getting Started


### Running Locally

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/koiic/stremio.git
   
   cd stremio
   
   create a virtual environment and activate it
   
   example: python3 -m venv venv or virtualenv venv
    source venv/bin/activate . (linux)
    venv\Scripts\activate (windows)
   
   create a .env file from the .env.example file and update the values accordingly
   
   cd backend
   
   pip install -r requirements.txt
   
   
    ```

   
Run the application:

   ```bash
   cd backend
   run make run_api
   or
   uvicorn main:app --reload
    ```

    For example: using the already added txt file

    ```bash
   
    ```
   you will see the logs in the terminal and you can test by navigating to 127.0.0.1:8000/docs.
   ```
  Optional - Run the tests:

   ```bash
   pytest
   ```
   
### Sample Documentation Image
![img.png](img.png)
