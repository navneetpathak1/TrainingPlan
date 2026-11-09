# Day 1 – FastAPI Training

## Topics Covered

### 1. FastAPI CRUD Operations (List of Dictionaries)

Implemented basic CRUD (Create, Read, Update, Delete) operations using FastAPI with an in-memory list of dictionaries.

**Concepts Covered:**
- Creating FastAPI endpoints (`GET`, `POST`, `PUT`, `DELETE`)
- Handling path parameters
- Using Python lists and dictionaries
- Request and response handling
- Understanding HTTP status codes
- Exception handling using `HTTPException`
- Writing Python functions with type hints
- Handling user input with structured input validation.

**Run the application:**

```bash
uv run fastapi dev .\November_09_2026\Learning_Topic\start.py
```

### 2. Connecting PostgreSQL Database with FastAPI

Configured a PostgreSQL database connection and integrated it with FastAPI.

**Concepts Covered:**
- Connecting PostgreSQL with FastAPI
- Using environment variables (`.env`) for database configuration
- Managing database connections
- Executing SQL queries
- Checking database connectivity through a health endpoint
- Handling database errors

**Setup:**

Create a `.env` file and configure the database credentials before starting the application.


**Run the application:**

```bash
uv run fastapi dev .\November_09_2026\Assignment\server.py
```

---

## Key Learnings

- Understanding FastAPI fundamentals.
- Implementing CRUD operations.
- Working with Python lists and dictionaries.
- Understanding HTTP methods and status codes.
- Connecting PostgreSQL with FastAPI.
- Managing sensitive configuration using `.env` files.

## Day 1 Status

Completed:
- FastAPI CRUD operations using `list[dict]`
- PostgreSQL database connection
- Environment variable configuration
- Database health-check endpoint