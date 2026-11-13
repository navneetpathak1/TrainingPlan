# Document Catalogue CRUD API

A RESTful API built using **FastAPI, Python, SQLAlchemy, and SQL database** to manage document catalogue records. The project supports CRUD operations, CSV-based bulk imports, database migrations, synthetic training datasets, and independent API testing.

## Project Overview

The Document Catalogue API manages document metadata for multiple tenants.

Each document contains information such as:
- Document ID
- Tenant ID
- Source ID
- Title
- Category
- Content Hash
- Version
- Created At

The system supports individual document management as well as bulk document imports through CSV files.

##  Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API framework |
| SQLAlchemy | ORM and database operations |
| SQLite / PostgreSQL | Database |
| Alembic | Database migrations |
| Pydantic | Request and response validation |
| Pandas | Training data preparation |
| CSV | Bulk document import |
| Pytest | API testing |
| HTTPX | Async API testing |
| UV | Python dependency management |

##  Database Design

### Documents Table

| Column | Data Type | Description |
|---|---|---|
| id | Integer | Primary key |
| tenant_id | String | Tenant identifier |
| source_id | String | Source document identifier |
| title | String | Document title |
| category | String | Document category |
| content_hash | String | Content hash |
| version | Integer | Document version |
| created_at | DateTime | Creation timestamp |

**Unique Constraint:**

`(tenant_id, source_id)`

This ensures that the same source document cannot be duplicated within a tenant.

Different tenants can have documents with the same source ID.

### Import Jobs Table

| Column | Data Type | Description |
|---|---|---|
| id | Integer | Primary key |
| status | String | Import status |
| accepted_count | Integer | Successfully imported records |
| rejected_count | Integer | Rejected records |

## CRUD Operations

The API provides the following document management endpoints.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents` | Create a document |
| GET | `/documents` | Retrieve all documents |
| GET | `/documents/{id}` | Retrieve a document by ID |
| PUT | `/documents/{id}` | Update a document |
| DELETE | `/documents/{id}` | Delete a document |

### Create Document

Example request:

```json
{
  "tenant_id": "tenant_A",
  "source_id": "data/file_101",
  "title": "FastAPI Documentation",
  "category": "Technical",
  "content_hash": "ABC123"
}
```

##  CSV Bulk Import

The project supports importing multiple documents through a CSV file.

### Import Endpoint

```http
POST /catalogue/import
```

### Training Dataset

A synthetic CSV dataset containing 100 records is used for testing the import functionality.

The dataset includes:

- Two synthetic tenants.
- Valid document records.
- Missing document IDs.
- Duplicate records.
- Invalid fields.
- Missing required values.
- Duplicate tenant and source combinations.

### Import Workflow

1. Upload the CSV file.
2. Read and validate CSV records.
3. Check mandatory fields.
4. Identify duplicate records.
5. Validate tenant and source identifiers.
6. Separate valid and invalid records.
7. Insert accepted records into the database.
8. Generate cleaned and rejected CSV files.
9. Create an import job record.
10. Return import statistics.

### Expected Import Response

```json
{
  "id": 1,
  "status": "completed",
  "accepted_count": 85,
  "rejected_count": 15
}
```

*Example response only; actual counts depend on the dataset.*

##  Database SQL and Migrations

The project uses SQLAlchemy for database interactions and Alembic for schema migrations.

### Initialize Alembic

```bash
uv run alembic init migrations
```

### Generate Migration

```bash
uv run alembic revision --autogenerate -m "create document tables"
```

### Apply Migrations

```bash
uv run alembic upgrade head
```

### Check Migration History

```bash
uv run alembic history
```

### Rollback Migration

```bash
uv run alembic downgrade -1
```

### SQL Operations

The database supports:

- CREATE TABLE
- INSERT
- SELECT
- UPDATE
- DELETE
- UNIQUE constraints
- Primary and foreign keys

##  Testing

Testing is maintained separately from the application code using Pytest.

### Test Structure

```text
tests/
│
├── conftest.py
├── test_document.py
└── test_catalogue_import.py
```

### Test Coverage

**Document CRUD Tests**
- Test document creation.
- Test document retrieval.
- Test retrieving a document by ID.
- Test document update.
- Test document deletion.
- Test retrieving a non-existent document.
- Test duplicate document creation.
- Test invalid request data.

**CSV Import Tests**
- Test successful CSV import.
- Test missing required fields.
- Test duplicate records.
- Test invalid data.
- Test accepted and rejected counts.
- Test cleaned CSV generation.
- Test rejected CSV generation.


##  Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Document_Catalogue
```

### Step 2: Install Dependencies

```bash
uv sync
```

### Step 3: Configure Database


### Step 4: Apply Database Migrations

```bash
uv run alembic upgrade head
```

### Step 5: Start the FastAPI Server

```bash
uv run uvicorn main:app --reload
```

### Step 6: Open API Documentation

Visit:

```text
http://127.0.0.1:8000/docs
```

##  Training Data Preparation

The project uses synthetic document data to validate API functionality.

Training data preparation includes:
1. synthetic CSV records.
2. Include two different tenants.
3. Identify missing values.
4. Detect duplicate records.
5. Validate column data types.
6. Clean invalid records.
7. Separate accepted and rejected records.
8. Export processed datasets.

Example Pandas operations:

## API Documentation

FastAPI automatically generates interactive API documentation.

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Key Features

- RESTful CRUD API.
- Multi-tenant document management.
- SQLAlchemy database integration.
- Alembic database migrations.
- Bulk CSV document import.
- Synthetic training dataset generation.
- Data validation and cleaning.
- Accepted and rejected CSV exports.
- Import job tracking.
- Separate Pytest test suite.
- Async database operations.

---

**Project:** Document Catalogue CRUD API  
**Backend:** Python + FastAPI  
**Database:** SQLAlchemy + SQL Database  
**Migration:** Alembic  
**Testing:** Pytest + HTTPX  
**Data Processing:** Pandas + CSV