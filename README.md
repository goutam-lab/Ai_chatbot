# Omnivio Chatbot Project

## Description
This project is a chatbot application backend built with FastAPI. It provides API endpoints to interact with the chatbot, including routes for chat functionality and integration with external services like OpenAI. The backend handles requests, processes chat messages, and returns responses to the frontend or other clients.

## How to Start the Chatbot Backend

### Prerequisites
- Python 3.7 or higher installed
- Dependencies installed (use `pip install -r backend/requirements.txt`)
- MongoDB running locally or accessible as configured in the project
- Environment variables configured in a `.env` file in the `backend` directory (e.g., OpenAI API key)

### Running the Backend Server
1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Start the FastAPI server using Uvicorn with the correct module path:
   ```bash
   uvicorn app.main:app --reload
   ```
3. The server will start and listen on `http://127.0.0.1:8000`. You can now interact with the chatbot API.

### Additional Notes
- The backend includes CORS middleware to allow cross-origin requests.
- API routes are organized under `/api` prefixes.
- Health check endpoint is available at `/health`.

Feel free to explore the API and integrate it with your frontend or other clients.
