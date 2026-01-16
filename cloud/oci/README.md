# Oracle Cloud Infrastructure (OCI)

This directory contains OCI-specific resources, applications, and configurations.

## Structure

```
oci/
├── functions/               # OCI Functions
├── container-instances/     # Container Instances
├── oke/                     # Oracle Kubernetes Engine
├── data-integration/        # Data Integration services
├── data-science/            # OCI Data Science
├── autonomous-db/           # Autonomous Database projects
└── scripts/                 # OCI CLI scripts
```

## Recommended Technologies

- **Compute**: Functions, Container Instances, OKE, Compute
- **Storage**: Object Storage, File Storage, Block Volumes
- **Database**: Autonomous Database, MySQL, NoSQL
- **Analytics**: Data Integration, Data Flow, Streaming
- **ML/AI**: Data Science, AI Services
- **IaC**: Resource Manager, Terraform

## Best Practices

- Use IAM policies with least privilege
- Implement compartment-based isolation
- Use Vault for secrets management
- Enable Audit service for logging
- Follow OCI security best practices
- Use tags for resource organization
