# Generative AI

This directory contains generative AI applications, LLM integrations, and AI-powered features.

## Structure

```
generative-ai/
├── applications/            # Gen AI applications
│   └── <app-name>/
│       ├── src/             # Application source code
│       ├── prompts/         # Prompt templates
│       ├── chains/          # LangChain/similar chains
│       ├── agents/          # AI agents
│       ├── tests/           # Tests
│       └── README.md        # Application docs
├── rag/                     # RAG (Retrieval Augmented Generation)
│   ├── embeddings/          # Embedding models and configs
│   ├── indexers/            # Document indexing
│   ├── retrievers/          # Retrieval strategies
│   └── pipelines/           # RAG pipelines
├── fine-tuning/             # Model fine-tuning
│   ├── datasets/            # Training datasets (metadata only)
│   ├── configs/             # Fine-tuning configurations
│   └── scripts/             # Fine-tuning scripts
├── evaluation/              # LLM evaluation
│   ├── benchmarks/          # Evaluation benchmarks
│   ├── metrics/             # Custom metrics
│   └── test-sets/           # Evaluation datasets
└── shared/                  # Shared utilities
    ├── llm-clients/         # LLM API clients
    ├── prompt-templates/    # Reusable prompts
    ├── guardrails/          # Safety guardrails
    └── tools/               # Agent tools
```

## Guidelines

### Creating a New Gen AI Application

1. Define clear use case and requirements
2. Design prompt templates carefully
3. Implement proper error handling
4. Add content safety guardrails
5. Monitor costs and latency
6. Test with diverse inputs

### Working with LLMs

1. Use environment variables for API keys
2. Implement retry logic with backoff
3. Cache responses when appropriate
4. Monitor token usage
5. Version control prompts

### Recommended Technologies

- **Frameworks**: LangChain, LlamaIndex, Semantic Kernel
- **LLM Providers**: OpenAI, Anthropic, Google, Azure OpenAI, Cohere
- **Vector Stores**: Pinecone, Weaviate, Chroma, Milvus, pgvector
- **Embedding Models**: OpenAI, Cohere, Sentence Transformers
- **Evaluation**: RAGAS, LangSmith, Promptfoo

### Best Practices

- Never hardcode API keys
- Implement rate limiting
- Add content moderation
- Log prompts and responses (with PII handling)
- Test edge cases and adversarial inputs
- Monitor for hallucinations
- Implement human-in-the-loop when needed
- Follow AI ethics guidelines
- Document model limitations
