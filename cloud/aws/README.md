# Amazon Web Services (AWS)

This directory contains AWS-specific resources, applications, and configurations.

## Structure

```
aws/
├── lambda/                  # AWS Lambda functions
├── ecs/                     # ECS/Fargate services
├── sagemaker/               # SageMaker ML projects
├── glue/                    # AWS Glue ETL jobs
├── step-functions/          # Step Functions workflows
├── cdk/                     # AWS CDK applications
├── sam/                     # SAM applications
└── scripts/                 # AWS CLI scripts
```

## Recommended Technologies

- **Compute**: Lambda, ECS, EKS, EC2
- **Storage**: S3, EBS, EFS
- **Database**: RDS, DynamoDB, Aurora, Redshift
- **Analytics**: Athena, EMR, Glue, Kinesis
- **ML/AI**: SageMaker, Bedrock, Comprehend
- **IaC**: CDK, SAM, CloudFormation

## Best Practices

- Use IAM roles with least privilege
- Enable CloudTrail for auditing
- Implement proper VPC security
- Use AWS Secrets Manager for secrets
- Tag resources consistently
- Monitor with CloudWatch
