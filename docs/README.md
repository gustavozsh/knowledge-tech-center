# Documentation

This directory contains project-wide documentation, guides, and standards.

## Structure

```
docs/
├── architecture/            # Architecture documentation
│   ├── decisions/           # Architecture Decision Records (ADRs)
│   ├── diagrams/            # System diagrams
│   └── overview.md          # System overview
├── guides/                  # How-to guides
│   ├── getting-started.md   # Getting started guide
│   ├── contributing.md      # Contribution guidelines
│   └── development.md       # Development guide
├── standards/               # Coding standards
│   ├── python.md            # Python standards
│   ├── javascript.md        # JavaScript/TypeScript standards
│   ├── go.md                # Go standards
│   └── api-design.md        # API design standards
├── runbooks/                # Operational runbooks
│   ├── deployment.md        # Deployment procedures
│   ├── incident-response.md # Incident response
│   └── troubleshooting.md   # Common issues
└── templates/               # Document templates
    ├── adr-template.md      # ADR template
    ├── readme-template.md   # README template
    └── runbook-template.md  # Runbook template
```

## Guidelines

### Writing Documentation

1. Use clear, concise language
2. Include examples and code snippets
3. Keep documentation up to date
4. Use diagrams for complex concepts
5. Link related documents

### Documentation Types

- **Tutorials**: Step-by-step learning guides
- **How-To Guides**: Task-oriented instructions
- **Reference**: Technical descriptions
- **Explanation**: Background and concepts

### Recommended Tools

- **Markdown**: Primary documentation format
- **Diagrams**: Mermaid, PlantUML, draw.io
- **API Docs**: OpenAPI/Swagger, AsyncAPI
- **Static Sites**: MkDocs, Docusaurus, VitePress

### Best Practices

- Document as you code
- Review documentation in PRs
- Use consistent formatting
- Include timestamps and authors
- Version documentation with code
- Test code examples
- Get feedback from users
