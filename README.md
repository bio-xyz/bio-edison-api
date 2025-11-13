# Bio Edison API

A FastAPI server that provides REST endpoints for interacting with the Edison Scientific platform. This API allows you to run various scientific tasks including literature searches, data analysis, precedent searches, chemistry tasks, and more.

## Features

- **Synchronous Task Execution**: Run tasks and wait for completion
- **Asynchronous Task Execution**: Start tasks and check status separately
- **Multiple Task Support**: Run multiple tasks in parallel
- **Task Continuation**: Follow up on previous tasks with additional queries
- **Comprehensive API Documentation**: Auto-generated OpenAPI docs
- **Health Checks**: Monitor service status
- **Docker Support**: Easy containerized deployment

## Quick Start

### Prerequisites

Choose one of the following deployment methods:
- **Option 1**: Python 3.11+ (for local installation)
- **Option 2**: Docker and Docker Compose (for containerized deployment)

You will also need:
- Edison Scientific API key

### Installation (Local)

For local Python installation:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bio-xyz/bio-edison-api
   cd bio-edison-api
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   If you're experiencing issues this way, attempt

   ```bash
    pip install fastapi==0.104.1 pydantic==2.5.0 python-dotenv==1.0.0
    pip install pytest==7.4.3 httpx==0.25.2
    pip install uvicorn\[standard\]==0.24.0 python-multipart==0.0.6
    pip install edison-client==0.7.6
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

Docker provides a containerized way to run the API without setting up Python locally.

#### Prerequisites for Docker
- Docker installed on your system
- Docker Compose (optional, for easier deployment)

#### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bio-xyz/bio-edison-api
   cd bio-edison-api
   ```

2. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

#### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t bio-edison-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 8000:8000 --name bio-edison-api bio-edison-api
   ```

3. **View logs:**
   ```bash
   docker logs -f bio-edison-api
   ```

4. **Stop and remove the container:**
   ```bash
   docker stop bio-edison-api
   docker rm bio-edison-api
   ```

The API will be available at `http://localhost:8000`

## Configuration

### Getting an Edison API Key

1. Visit the [Edison Scientific platform](https://platform.edisonscientific.com/profile)
2. Sign up for an account or log in
3. Go to your profile page
4. Generate an API key

### Authentication

All Edison API endpoints require authentication via Bearer token in the Authorization header:

```bash
Authorization: Bearer your-edison-api-key-here
```

The API key should be passed with every request to Edison endpoints. No server-side configuration file is needed.

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Health Checks
- `GET /` - Welcome message
- `GET /health` - General health check
- `GET /api/v1/edison/health` - Edison service connectivity check

### Edison Tasks

#### Available Job Types
- `GET /api/v1/edison/jobs/available` - List all available job types

#### Synchronous Execution
- `POST /api/v1/edison/run/sync` - Run single task synchronously
- `POST /api/v1/edison/run/sync/multiple` - Run multiple tasks synchronously

#### Asynchronous Execution
- `POST /api/v1/edison/run/async` - Start single task asynchronously
- `POST /api/v1/edison/run/async/multiple` - Start multiple tasks asynchronously
- `GET /api/v1/edison/task/{task_id}/status` - Check task status

#### Task Continuation
- `POST /api/v1/edison/run/continuation/sync` - Run follow-up questions on previous tasks synchronously
- `POST /api/v1/edison/run/continuation/async` - Start follow-up task asynchronously

## Usage Examples

### 1. Synchronous Literature Search

```bash
curl -X POST "http://localhost:8000/api/v1/edison/run/sync" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-edison-api-key-here" \
  -d '{
    "name": "LITERATURE",
    "query": "Which neglected diseases had a treatment developed by artificial intelligence?"
  }'
```

### 2. Asynchronous Precedent Search

Start the task:
```bash
curl -X POST "http://localhost:8000/api/v1/edison/run/async" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-edison-api-key-here" \
  -d '{
    "name": "PRECEDENT",
    "query": "Has anyone tested therapeutic exerkines in humans or NHPs?"
  }'
```

Check status:
```bash
curl -X GET "http://localhost:8000/api/v1/edison/task/{task_id}/status" \
  -H "Authorization: Bearer your-edison-api-key-here"
```

### 3. Multiple Tasks

```bash
curl -X POST "http://localhost:8000/api/v1/edison/run/sync/multiple" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-edison-api-key-here" \
  -d '{
    "tasks": [
      {
        "name": "LITERATURE",
        "query": "What are the latest treatments for diabetes?"
      },
      {
        "name": "PRECEDENT",
        "query": "Has anyone used AI for drug discovery in diabetes?"
      }
    ]
  }'
```

### 4. Task Continuation

Synchronous (wait for completion):
```bash
curl -X POST "http://localhost:8000/api/v1/edison/run/continuation/sync?continued_job_id=previous-task-id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-edison-api-key-here" \
  -d '{
    "name": "LITERATURE",
    "query": "From the previous answer, what are the side effects of those treatments?"
  }'
```

Asynchronous (get task ID):
```bash
curl -X POST "http://localhost:8000/api/v1/edison/run/continuation/async?continued_job_id=previous-task-id" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-edison-api-key-here" \
  -d '{
    "name": "LITERATURE",
    "query": "From the previous answer, what are the side effects of those treatments?"
  }'
```

## Available Job Types

| Job Type | Description |
|----------|-------------|
| `LITERATURE` | Literature Search - Query scientific databases with high-accuracy, cited responses |
| `ANALYSIS` | Data Analysis - Analyze biological datasets and answer research questions |
| `PRECEDENT` | Precedent Search - Find if specific research has been done before |
| `MOLECULES` | Chemistry Tasks - Molecular design and synthesis planning |
| `DUMMY` | Dummy Task - For testing purposes |

