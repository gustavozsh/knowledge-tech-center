# Apps Factory

A comprehensive monorepo structure for developing multiple types of software applications including APIs, data engineering pipelines, data science projects, generative AI applications, utility libraries, infrastructure, and DevOps configurations.

## 🏗️ Repository Structure

```
apps-factory/
├── apis/                    # REST/GraphQL APIs and backend services
├── data-engineering/        # Data pipelines, ETL processes
├── data-science/            # ML models, experiments, notebooks
├── generative-ai/           # Gen AI applications, LLM integrations
├── utils/                   # Shared utility functions and libraries
├── infrastructure/          # Infrastructure as Code (Terraform, Pulumi, etc.)
├── devops/                  # CI/CD, Docker, Kubernetes configurations
└── docs/                    # Project documentation
```

## 📁 Directory Overview

| Directory | Purpose | Technologies |
|-----------|---------|--------------|
| [`apis/`](apis/) | Backend services, REST/GraphQL APIs | FastAPI, Express, Spring Boot, Gin |
| [`data-engineering/`](data-engineering/) | Data pipelines, ETL, transformations | Airflow, Spark, dbt, Kafka |
| [`data-science/`](data-science/) | ML models, experiments, analysis | PyTorch, TensorFlow, scikit-learn |
| [`generative-ai/`](generative-ai/) | LLM apps, RAG, AI agents | LangChain, LlamaIndex, OpenAI |
| [`utils/`](utils/) | Shared libraries, common utilities | Python, JavaScript, Go packages |
| [`infrastructure/`](infrastructure/) | Cloud infrastructure code | Terraform, Pulumi, Kubernetes |
| [`devops/`](devops/) | CI/CD, containers, monitoring | GitHub Actions, Docker, Prometheus |
| [`docs/`](docs/) | Documentation and guides | Markdown, diagrams |

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/gustavozsh/apps-factory.git
   cd apps-factory
   ```

2. **Choose your project directory** based on the type of software you're building

3. **Follow the directory-specific README** for setup instructions

4. **Read the [Getting Started Guide](docs/guides/getting-started.md)** for detailed instructions

## 📖 Documentation

- [Getting Started](docs/guides/getting-started.md) - Quick start guide
- [Contributing](docs/guides/contributing.md) - How to contribute
- [Templates](docs/templates/) - Document and project templates

## 🛠️ Development

### Prerequisites

- Git
- Language-specific tools based on your project (Python, Node.js, Go, etc.)
- Docker (recommended)
- Make (optional, for automation)

### Project Structure

Each project within a directory should follow this structure:

```
<project-name>/
├── src/              # Source code
├── tests/            # Tests
├── docs/             # Documentation
├── Dockerfile        # Container configuration (if applicable)
└── README.md         # Project documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/guides/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details