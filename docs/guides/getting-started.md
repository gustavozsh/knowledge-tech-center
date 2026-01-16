# Getting Started

Welcome to Apps Factory! This guide will help you get started with the repository.

## Prerequisites

- Git
- A code editor (VS Code recommended)
- Language-specific tools based on your project:
  - **Python**: Python 3.9+, pip, virtualenv
  - **Node.js**: Node 18+, npm or yarn
  - **Go**: Go 1.21+
  - **Java**: JDK 17+, Maven or Gradle
  - **Rust**: Rust 1.70+

## Repository Structure

```
apps-factory/
├── apis/                    # REST/GraphQL APIs and backend services
├── cloud/                   # Cloud provider-specific resources
│   ├── aws/                 # Amazon Web Services
│   ├── azure/               # Microsoft Azure
│   ├── gcp/                 # Google Cloud Platform
│   └── oci/                 # Oracle Cloud Infrastructure
├── data-engineering/        # Data pipelines and ETL processes
├── data-science/            # ML models and experiments
├── generative-ai/           # Gen AI applications
├── utils/                   # Shared utility functions
├── infrastructure/          # Infrastructure as Code
├── devops/                  # CI/CD and operational tooling
└── docs/                    # Documentation
```

## Creating a New Project

### 1. Choose the Right Directory

Select the appropriate directory based on your project type:

| Project Type | Directory |
|-------------|-----------|
| API/Backend Service | `apis/` |
| AWS Resources | `cloud/aws/` |
| Azure Resources | `cloud/azure/` |
| GCP Resources | `cloud/gcp/` |
| OCI Resources | `cloud/oci/` |
| Data Pipeline/ETL | `data-engineering/` |
| ML Model/Experiment | `data-science/` |
| Gen AI Application | `generative-ai/` |
| Shared Library | `utils/` |
| Multi-Cloud IaC | `infrastructure/` |
| CI/CD/Containers | `devops/` |

### 2. Create Your Project Directory

```bash
mkdir -p apis/my-service
cd apis/my-service
```

### 3. Initialize Your Project

Follow the language/framework specific initialization:

**Python (FastAPI example)**:
```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
```

**Node.js (Express example)**:
```bash
npm init -y
npm install express
```

### 4. Add Documentation

Create a README.md in your project directory with:
- Project description
- Setup instructions
- Usage examples
- API documentation (if applicable)

### 5. Add Tests

Create a `tests/` directory and add appropriate tests.

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests locally
4. Create a pull request
5. Request review
6. Merge after approval

## Need Help?

- Check the specific directory README for detailed guidelines
- Review existing projects for examples
- Read the architecture documentation in `docs/architecture/`
