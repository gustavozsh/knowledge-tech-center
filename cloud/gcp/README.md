# Google Cloud Platform (GCP)

This directory contains GCP-specific resources, applications, and configurations.

## Structure

```
gcp/
├── cloud-functions/         # Cloud Functions
├── cloud-run/               # Cloud Run services
├── gke/                     # Google Kubernetes Engine
├── dataflow/                # Dataflow pipelines
├── bigquery/                # BigQuery projects
├── vertex-ai/               # Vertex AI ML projects
├── composer/                # Cloud Composer (Airflow)
└── scripts/                 # gcloud CLI scripts
```

## Recommended Technologies

- **Compute**: Cloud Functions, Cloud Run, GKE, Compute Engine
- **Storage**: Cloud Storage, Filestore
- **Database**: Cloud SQL, Firestore, Spanner, BigQuery
- **Analytics**: BigQuery, Dataflow, Dataproc, Pub/Sub
- **ML/AI**: Vertex AI, AI Platform, AutoML
- **IaC**: Deployment Manager, Terraform, Config Connector

## Best Practices

- Use Service Accounts with minimal permissions
- Enable Cloud Audit Logs
- Implement VPC Service Controls
- Use Secret Manager for secrets
- Follow Google Cloud security best practices
- Use labels for resource organization
