# Tachyon Evaluation Service

A FastAPI-based service for managing and evaluating datasets and models.

## Features

- Dataset management
- Golden data management
- Model evaluation
- MongoDB integration
- Retry mechanism for database operations

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the service:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── core/           # Core functionality and exceptions
├── db/            # Database configuration
├── schemas/       # Pydantic models
├── services/      # Business logic
└── main.py        # Application entry point
```

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tachyon_eval_service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tachyon_eval

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Security
API_KEY_HEADER=X-API-Key
API_KEY=your-secret-api-key-here

# Metrics Configuration
METRICS_RETENTION_DAYS=30
METRICS_AGGREGATION_INTERVAL=1h

# Evaluation Configuration
MAX_CONCURRENT_EVALUATIONS=10
EVALUATION_TIMEOUT_SECONDS=3600
```

## Running the Application

1. Start MongoDB:
```bash
mongod --dbpath /path/to/data/directory
```

2. Run the application:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Datasets
- `GET /api/v1/usecases/{usecase_id}/datasets` - List datasets
- `GET /api/v1/usecases/{usecase_id}/datasets/{dataset_id}` - Get dataset
- `POST /api/v1/usecases/{usecase_id}/datasets` - Create dataset
- `DELETE /api/v1/usecases/{usecase_id}/datasets/{dataset_id}` - Delete dataset

### Evaluations
- `GET /api/v1/usecases/{usecase_id}/evaluations` - List evaluations
- `GET /api/v1/usecases/{usecase_id}/evaluations/{evaluation_id}` - Get evaluation
- `POST /api/v1/usecases/{usecase_id}/evaluations` - Create evaluation
- `PUT /api/v1/usecases/{usecase_id}/evaluations/{evaluation_id}` - Update evaluation
- `DELETE /api/v1/usecases/{usecase_id}/evaluations/{evaluation_id}` - Delete evaluation
- `PATCH /api/v1/usecases/{usecase_id}/evaluations/{evaluation_id}/status` - Update evaluation status

### Metrics
- `GET /api/v1/usecases/{usecase_id}/metrics` - Get usecase metrics
- `GET /api/v1/usecases/{usecase_id}/datasets/{dataset_id}/metrics` - Get dataset metrics
- `GET /api/v1/usecases/{usecase_id}/evaluations/{evaluation_id}/metrics` - Get evaluation metrics

## Error Handling

The service includes comprehensive error handling for:
- Validation errors (400 Bad Request)
- Not found errors (404 Not Found)
- Database errors (500 Internal Server Error)
- Authentication errors (401 Unauthorized)

## Retry Mechanism

The service implements a retry mechanism for database operations with:
- Exponential backoff
- Configurable retry attempts
- Specific exception handling

## Security

- API key authentication
- CORS middleware
- Input validation
- Secure environment variable handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 