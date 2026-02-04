# CLAUDE.md

## Project Overview

**Apps Factory** - A comprehensive monorepo for developing APIs, data engineering pipelines, data science projects, generative AI applications, and cloud infrastructure. Currently contains two production-ready data extraction APIs (Google Analytics 4 and Twitter/X to BigQuery).

## Quick Reference

| Directory | Purpose |
|-----------|---------|
| `apis/` | REST APIs (GA4, Twitter extraction) |
| `cloud/` | Cloud provider resources (AWS, Azure, GCP, OCI) |
| `data-engineering/` | Data pipelines, ETL processes |
| `data-science/` | ML models, experiments |
| `generative-ai/` | LLM apps, AI agents |
| `infrastructure/` | Terraform, Pulumi, Kubernetes |
| `devops/` | CI/CD, Docker, monitoring |
| `resources/` | Learning materials, papers, tutorials |
| `utils/` | Shared utility libraries |
| `docs/` | Documentation and guides |

## Technology Stack

- **Language**: Python 3.11-3.12
- **Web Framework**: Flask 3.0+
- **Server**: Gunicorn (8 threads)
- **Cloud**: Google Cloud Platform (Cloud Run, BigQuery, Secret Manager, Composer)
- **Containerization**: Docker (multi-stage builds)
- **Orchestration**: Apache Airflow via Cloud Composer

## Key Entry Points

- `/apis/google-analytics-4/main.py` - GA4 Flask API
- `/apis/google-analytics-4/ga4.py` - GA4 data extraction logic
- `/apis/twitter/main.py` - Twitter Flask API
- `/apis/twitter/config.py` - Twitter configuration

## Development Commands

```bash
# Run GA4 API locally
cd apis/google-analytics-4
pip install -r requirements.txt
python main.py

# Run Twitter API locally
cd apis/twitter
pip install -r requirements.txt
python main.py

# Build Docker images
docker build -t ga4-api apis/google-analytics-4/
docker build -t twitter-api apis/twitter/
```

## Code Style & Conventions

### Formatting (from .editorconfig)
- **Python**: 4-space indentation
- **JavaScript/TypeScript/JSON**: 2-space indentation
- **YAML**: 2-space indentation
- **Go/Makefile**: Tabs
- **Shell scripts**: 2-space indentation
- **Line endings**: LF (Unix-style)
- **Trailing whitespace**: Trimmed
- **Final newline**: Required

### Commit Messages
Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `refactor:` - Code refactoring
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

### Project Structure Pattern
```
<project-name>/
├── src/              # Source code
├── tests/            # Tests
├── docs/             # Documentation
├── Dockerfile        # Container configuration
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

## Architecture Pattern

```
Cloud Composer (Airflow)
    ↓ (schedules daily)
Cloud Run (Flask APIs)
    ↓
BigQuery (Data Warehouse)
    ↓
Secret Manager (Credentials)
```

## Environment Variables

### GA4 API
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GA4_PROPERTY_ID` - GA4 property identifier
- `BIGQUERY_DATASET` - Target BigQuery dataset

### Twitter API
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `TWITTER_BEARER_TOKEN` - Twitter API bearer token (or via Secret Manager)
- `BIGQUERY_DATASET` - Target BigQuery dataset

## Important Notes

1. **APIs are Cloud Run-ready** - Use provided Dockerfiles for deployment
2. **Secret Manager integration** - Store credentials securely, not in environment
3. **Airflow DAGs included** - For scheduling daily data extractions
4. **Pin dependency versions** - Always specify versions in requirements.txt
5. **Update READMEs** - Document changes in relevant directory READMEs

## Testing

Run tests from the project root or specific API directories:
```bash
pytest tests/
```

## Documentation

- [Getting Started](docs/guides/getting-started.md)
- [Contributing Guidelines](docs/guides/contributing.md)
- [Templates](docs/templates/)
