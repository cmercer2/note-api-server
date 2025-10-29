# Note API Server

This project is a Flask application that provides endpoints for managing freezer contents and meal plans. It is designed to parse incoming requests, store the data, and forward it to specified webhooks.

## Project Structure

```
note-api-server
├── src
│   ├── server.py          # Main Flask application with endpoints
│   ├── config.py          # Configuration variables for webhooks
│   └── __init__.py        # Marks the directory as a Python package
├── Dockerfile              # Instructions for building the Docker image
├── docker-compose.yml      # Defines services and configurations for Docker
├── requirements.txt        # Lists Python dependencies
├── .env                    # Environment variables for the Docker container
├── .dockerignore           # Files to ignore when building the Docker image
└── README.md               # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd note-api-server
   ```

2. **Create a `.env` file:**
   Define your environment variables in the `.env` file. For example:
   ```
   FREEZER_PLUGIN_WEBHOOK_URL=<your_freezer_webhook_url>
   MEAL_PLAN_WEBHOOK_URL=<your_meal_plan_webhook_url>
   ```

3. **Build and run the application using Docker Compose:**
   ```
   docker-compose up --build
   ```

4. **Access the application:**
   The Flask application will be running at `http://localhost:5000`.

## Usage

- **Freezer List Endpoint:**
  - **POST /freezer-list**: Send a bulleted list of freezer contents to this endpoint. The application will parse the list and forward it to the specified webhook.
  - **GET /freezer-list**: Retrieve the last received freezer list.

- **Meal Plan Endpoint:**
  - **POST /meal-plan**: Send a bulleted list of meal plans for the week. The application will parse the list and forward it to the specified webhook.
  - **GET /meal-plan**: Retrieve the last received meal plan.

## Dependencies

The project requires the following Python packages, which are listed in `requirements.txt`:
- Flask
- requests

## Docker

This project uses Docker for containerization. The `Dockerfile` and `docker-compose.yml` file are provided to facilitate the setup and deployment of the application in a Docker environment.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.