# DocAPI Document Processing API

A FastAPI-based service for processing medical documents and extracting patient information.

## Features

- Document OCR text reconstruction from bounding boxes
- Patient name extraction from medical documents
- Configurable settings via environment variables
- Custom exception handling
- Comprehensive test coverage (94%)

## Setup

You can set up the project in two ways: using **uv** (recommended for local development) or using **Docker**.

```bash
# Clone the repository
git clone https://github.com/LavalAlexandre/docAPI.git
cd docAPI
```

### Option 1: Setup with uv (Recommended)

#### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

#### Installation

```bash
# Install dependencies
uv sync

# Optional: Create .env file for custom configuration
cp .env.example .env

# Optional: Install pre-commit hooks
uv run pre-commit install
```

#### Launch the API

```bash
# Development mode (with hot reload)
uv run fastapi dev

# Production mode
uv run fastapi run src/main.py --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Option 2: Setup with Docker

#### Prerequisites

- Docker installed on your system

#### Build the Docker Image

```bash
# Build the image
docker build -t docapi-api .
```

#### Launch the API

```bash
# Development mode (with hot reload)
docker run -p 8000:8000 \
  -v $(pwd)/src:/app/src \
  docapi-api \
  fastapi dev src/main.py --host 0.0.0.0 --port 8000

# Production mode
docker run -p 8000:8000 docapi-api

# With custom environment variables
docker run -p 8000:8000 \
  -e DOCAPI_ENABLE_FEMININE_TITLES=true \
  docapi-api
```

The API will be available at `http://localhost:8000`

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Configuration

The application can be configured via environment variables. All variables are prefixed with `DOCAPI_`.

See `.env.example` for available configuration options:

- `DOCAPI_OCR_Y_THRESHOLD`: Y-axis threshold for word grouping (default: 0.01)
- `DOCAPI_ENABLE_FEMININE_TITLES`: Support feminine medical titles (default: false)

## Development

### Running Tests

```bash
# Run all tests with uv
uv run pytest

# With coverage report
uv run pytest --cov=src --cov-report=term

# With Docker
docker run --rm docapi-api pytest -v --cov=src --cov-report=term
```

### Code Quality Tools

```bash
# Run linter
uv run ruff check .

# Fix linting issues automatically
uv run ruff check --fix .

# Format code
uv run ruff format .

# Type checking
uv run mypy src

# Run all checks with validation script
./validate.sh
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # FastAPI application entry point
├── config.py            # Application settings and configuration
├── exceptions.py        # Custom exception classes
├── data/                # Data access layer
│   ├── documents.py     # Fake document database
├── models/              # Pydantic models
│   ├── document.py      # Document, Page, Word, BoundingBox models
├── operations/          # Business logic layer
│   ├── documents.py     # Document processing operations
└── routers/             # API routes
    ├── documents.py     # Document endpoints
tests/                   # Test suite
├── test_config.py
├── test_operations.py
└── test_routers.py
```

## API Endpoints

### `GET /`
Health check endpoint.

### `GET /documents`
List all documents.

### `GET /documents/{document_id}`
Get a specific document by ID.

### `GET /documents/{document_id}/patient-name`
Get the extracted patient name from a document.

## Patient Name Extraction Algorithm

The core feature of this API is extracting patient names from medical documents. The extraction uses a **heuristic-based approach** that identifies capitalized words while filtering out medical titles, honorifics, and sentence-starting words.

### How It Works

#### Step 1: Text Reconstruction
First, the document's OCR words (with bounding boxes) are reconstructed into an ordered list:
- Words are grouped into lines based on vertical position (y-coordinate)
- Within each line, words are sorted left-to-right (x-coordinate)
- This produces a reading-order list of words

#### Step 2: Name Extraction Heuristic

The algorithm scans through the ordered words and applies the following **filtering rules**:

##### ✅ **A patient name must:**
1. **Start with an uppercase letter** (e.g., "Jean", "DUPONT")
2. **Be 1-2 words long** (e.g., "Jean DUPONT" or "Martin")
3. **Not be the first word** of the document

##### ❌ **A patient name cannot:**
1. **Follow a sentence-ending punctuation** (`.`, `!`, `?`)
   - Example: "Consultation terminée. Jean" → "Jean" is rejected (starts a new sentence)

2. **Follow a medical title** (doctor, professor, specialist, etc.)
   - Example: "Docteur Nicolas JACQUES" → "Nicolas JACQUES" is rejected
   - **Supports 35+ French medical titles** (e.g., docteur, chirurgien, cardiologue, etc.)
   - **Optional feminine title support** (e.g., doctoresse, chirurgienne, réanimatrice)
   - When a title is detected, the algorithm **skips the next word** as well

3. **Be a medical title itself**
   - Example: "Chirurgien Martin" → "Chirurgien" is rejected

4. **Be an honorific** (Monsieur, Madame, etc.)
   - Example: "Madame Clara Martin" → "Madame" is skipped, but "Clara Martin" is valid

#### Step 3: Two-Word Name Detection
- If a valid name candidate is found, the algorithm checks if the **next word is also capitalized**
- If yes, it returns both words as a full name: `"Jean DUPONT"`
- If no, it returns just the single word: `"Martin"`

### Example Walkthrough

**Input document text:**
```
"J'ai bien revu en consultation Monsieur Jean DUPONT pour une douleur à la hanche droite. Docteur Nicolas JACQUES"
```

**Processing:**

| Word | Rule Check | Result |
|------|------------|--------|
| `J'ai` | First word | ❌ Skip |
| `bien` | Lowercase | ❌ Skip |
| `revu` | Lowercase | ❌ Skip |
| `en` | Lowercase | ❌ Skip |
| `consultation` | Lowercase | ❌ Skip |
| `Monsieur` | Honorific | ❌ Skip |
| `Jean` | ✅ Capitalized, not after title/punctuation | Check next word... |
| `DUPONT` | ✅ Also capitalized | **✅ Return "Jean DUPONT"** |

**Output:** `"Jean DUPONT"`

**Why "Nicolas JACQUES" is NOT extracted:**
- "Nicolas" follows "Docteur" (a medical title)
- The algorithm skips both "Nicolas" and "JACQUES"

### Configuration

The extraction behavior can be customized via environment variables:

```bash
# Enable feminine medical titles (doctoresse, chirurgienne, etc.)
DOCAPI_ENABLE_FEMININE_TITLES=true
```

### Limitations & Edge Cases

**Known limitations:**
- **Language-specific**: Designed for French medical documents
- **Case-sensitive**: Requires proper capitalization of names
- **Simple heuristic**: May fail with:
  - All-caps documents
  - Unusual name formats (e.g., "Marie-Claire", hyphenated names)
  - Names at the start of sentences after punctuation
  - Documents with multiple patient names (returns first match only)

**Future improvements:**
- Support for hyphenated names
- Context-aware extraction (patient vs. doctor identification)
- Additional api routes
- Implement database

### Related Code

- **Algorithm implementation**: `src/operations/documents.py::extract_patient_name_from_words()`
- **Configuration**: `src/config.py::PatientNameExtractionConfig`
- **Tests**: `tests/test_operations.py`

## Architecture

The project follows a clean architecture pattern:

1. **Routers** (`routers/`): Handle HTTP requests/responses, validate input, convert exceptions to HTTP errors
2. **Operations** (`operations/`): Contain business logic, use domain exceptions
3. **Models** (`models/`): Define data structures using Pydantic
4. **Data** (`data/`): Data access layer (currently in-memory, can be replaced with a database)
5. **Config** (`config.py`): Centralized configuration management

## TODO

- [ ] Add logging throughout the application
- [ ] Implement real database layer
- [ ] Add authentication/authorization
- [ ] Add metrics and monitoring
- [ ] Add more exception handling and implement additional custom exceptions as needed
