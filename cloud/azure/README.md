# Microsoft Azure

This directory contains Azure-specific resources, applications, and configurations.

## Structure

```
azure/
├── functions/               # Azure Functions
├── app-service/             # App Service applications
├── aks/                     # Azure Kubernetes Service
├── data-factory/            # Data Factory pipelines
├── synapse/                 # Synapse Analytics
├── ml/                      # Azure Machine Learning
├── bicep/                   # Bicep templates
└── scripts/                 # Azure CLI scripts
```

## Recommended Technologies

- **Compute**: Functions, App Service, AKS, VMs
- **Storage**: Blob Storage, Files, Data Lake
- **Database**: SQL Database, Cosmos DB, PostgreSQL
- **Analytics**: Synapse, Data Factory, Stream Analytics
- **ML/AI**: Azure ML, OpenAI Service, Cognitive Services
- **IaC**: Bicep, ARM Templates, Terraform

## Best Practices

- Use Managed Identities for authentication
- Implement Azure Policy for governance
- Use Key Vault for secrets management
- Enable Azure Monitor and Log Analytics
- Follow Azure Well-Architected Framework
- Use resource groups for organization
