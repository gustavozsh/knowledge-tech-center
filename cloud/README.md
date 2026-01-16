# Cloud

This directory contains cloud-specific resources, configurations, and projects organized by cloud provider.

## Structure

```
cloud/
├── aws/                     # Amazon Web Services
├── azure/                   # Microsoft Azure
├── gcp/                     # Google Cloud Platform
└── oci/                     # Oracle Cloud Infrastructure
```

## Guidelines

### Organizing Cloud Resources

Each cloud provider directory can contain:
- Cloud-specific applications and services
- Provider-specific configurations
- Cloud-native tooling and scripts
- Migration scripts and utilities

### Best Practices

- Keep provider-specific code isolated
- Use environment variables for credentials
- Follow each provider's security best practices
- Document provider-specific requirements
- Use official SDKs and CLIs

### Cross-Cloud Considerations

For multi-cloud or cloud-agnostic solutions:
- Consider using the `infrastructure/` directory with tools like Terraform or Pulumi
- Document cloud-specific variations
- Implement abstraction layers when appropriate
