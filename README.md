# AI Tour Planner 🗺️

## Prerequisites

- Python 3.11+
- Docker
- MongoDB
- Ollama

## Quick Start

### 1. Environment Setup

##### Create virtual environment

```shell

python -m venv venv
```

##### Activate (Linux/Mac)

```shell
source venv/bin/activate
```
### 2. Install lib/packages
```shell
pip install -r requirements.py
``` 

### 3. Start MongoDB (Linux/Mac)

```shell
sudo systemctl restart mongod
```

### 4. Setting up ollama:

##### pull llama3 llm for enabeling chat:
```shell
ollama pull llama3
```

##### Pull the Embeddings model:

```shell
ollama pull nomic-embed-text
```

### 5. Run using Docker

```shell
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```

### 6. Adding serpapi for searching info. form google
```shell
export SERPAPI_API_KEY=***
```

### 7. Start Backend
```shell
cd backend
uvicorn main:app --reload --port 8000
```

### 8. Start Frontend
```shell
cd frontend
streamlit run app.py
```


## Application Structure

### Backend

- **main.py**: FastAPI application with endpoints for:
  - User authentication
  - Chat message storage
  - User preferences
  - Database operations

- **database.py**: Database connections and operations for:
  - MongoDB (user data, chat history)
  - Neo4j (user preferences)
  - PgVector (AI knowledge base)

- **auth_utils.py**: Authentication utilities:
  - Password hashing
  - Password verification
  - Token management

- **schemas.py**: Pydantic models for:
  - User creation/login
  - Chat messages
  - API responses

### Frontend

- **app.py**: Streamlit interface containing:
  - User authentication UI
  - Chat interface
  - Session management
  - API integrations

- **agent.py**: AI agent configuration:
  - LLM setup
  - Tool integration
  - Knowledge base connection
  - Chat processing

---

## API Endpoints

- **POST /register** - User registration
- **POST /login** - User authentication
- **POST /chat/** - Store chat messages
- **POST /preferences/** - Store user preferences
- **GET /preferences/{user_id}** - Retrieve user preferences

