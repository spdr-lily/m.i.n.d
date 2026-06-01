# M.I.N.D Project - Quick Start Guide

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 16+ (or Docker)
- Git

### 2. Environment Setup

#### Windows (PowerShell)
```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
Copy-Item .env.example -Destination .env
```
#### Option B: Local PostgreSQL
1. Install PostgreSQL 16
2. Create database and user:
   ```sql
   CREATE ROLE mind_user WITH LOGIN PASSWORD 'mind_password';
   CREATE DATABASE mind_db OWNER mind_user;
   ```
3. Update `.env` with your database connection string

### 4. Database Migrations

```bash
# Create initial schema
alembic upgrade head

# Verify migrations applied
psql postgresql://mind_user:mind_137_Cmspelo@localhost:5432/mind -c "\dt"
```

### 5. Run the Application

```bash
# Start FastAPI development server
uvicorn app.main:app --reload

# API docs available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - OpenAPI JSON: http://localhost:8000/openapi.json
```

### 6. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_criteria_evaluator.py -v

# Run only integration tests
pytest tests/integration/ -v -m integration
```

## 📁 Project Structure

Key directories:
- **app/** — Main application code
  - **core/** — Config, exceptions, database
  - **models/** — SQLAlchemy ORM models
  - **schemas/** — Pydantic DTOs
  - **services/** — Business logic
  - **repositories/** — Data access layer
  - **ml/** — Bayesian inference pipelines
  - **api/** — FastAPI routes
  - **security/** — Auth & encryption

- **tests/** — Test suite
  - **unit/** — Component tests
  - **integration/** — Workflow tests

- **alembic/** — Database migrations
- **migrations/** — SQL scripts

See [STRUCTURE.md](STRUCTURE.md) for detailed documentation.

## 🔑 Key Development Patterns

### Adding a New Endpoint

1. Create Pydantic schema in `app/schemas/`
2. Create repository methods in `app/repositories/`
3. Create service logic in `app/services/`
4. Create API route in `app/api/`
5. Write tests in `tests/`

### Adding a New Database Model

1. Define SQLAlchemy model in `app/models/`
2. Create migration: `alembic revision --autogenerate -m "Add new table"`
3. Create Pydantic schema
4. Create repository methods
5. Implement service logic

### Clinical Development

When implementing clinical features:
- Always reference DSM-5-TR or ICD-11 codes
- Include human-in-the-loop validation steps
- Test with synthetic clinical data (not real patient records)
- Log all diagnostic calculations for audit trail
- Use UUIDs for patient identifiers (LGPD compliance)

## 🧪 Testing

### Create a Test File
```python
import pytest

@pytest.mark.unit
def test_my_feature(db_session):
    """Test description with clinical context if relevant"""
    # Arrange
    # Act
    # Assert
    assert True
```

### Run Tests with Markers
```bash
pytest -m unit              # Run unit tests only
pytest -m integration       # Run integration tests only
pytest -m "not slow"        # Skip slow tests
```

## 📊 Code Quality

### Format Code
```bash
black app/ tests/
isort app/ tests/
```

### Check for Issues
```bash
flake8 app/ tests/
pylint app/
mypy app/
```

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # View report
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Migration Issues
```bash
# Check migration status
alembic current
alembic history

# Downgrade last migration
alembic downgrade -1

# View migration script
cat alembic/versions/001_*.py
```

### Import Errors
```bash
# Verify virtual environment is activated
python -c "import app"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Resources

### Documentation Files
- [STRUCTURE.md](STRUCTURE.md) — Detailed project structure
- [README.md](README.md) — Full project specification
- [.agent.md](.agent.md) — AI agent configuration
- [.instructions.md](.instructions.md) — Development guidelines

### External Resources
- [DSM-5-TR Official](https://dsm.psychiatryonline.org/)
- [ICD-11 Browser](https://icd.who.int/browse11/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)

### Clinical References
- [MIMIC-IV Dataset](https://mimic.physionet.org/)
- [Brazilian LGPD](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
- [UMLS Metathesaurus](https://www.nlm.nih.gov/research/umls/)

## 🚢 Deployment

### Docker Build
```bash
# Build Docker image
docker build -t mind-cdss:latest .

# Run container
docker run -p 8000:8000 mind-cdss:latest
```

### Environment Variables (Production)
- Set `DEBUG=False`
- Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- Configure proper `DATABASE_URL`
- Set `CORS_ORIGINS` appropriately
- Enable HTTPS only

See [.env.example](.env.example) for all configuration options.

## 💡 Next Steps

1. ✅ Environment set up complete
2. ⬜ Create initial database models (see [STRUCTURE.md](STRUCTURE.md))
3. ⬜ Implement patient CRUD endpoints
4. ⬜ Build Bayesian inference engine
5. ⬜ Implement diagnostic calculation service
6. ⬜ Add authentication & authorization
7. ⬜ Create clinical assessment scales
8. ⬜ Full API documentation

## 📞 Support

For issues or questions:
1. Check [STRUCTURE.md](STRUCTURE.md) for architecture details
2. Review [.instructions.md](.instructions.md) for development patterns
3. Check test files for usage examples
4. Consult [.agent.md](.agent.md) for project guidelines

---

**Last Updated:** 2024-05-29  
**Status:** MVP Phase - Database Schema & Initial Setup Complete
