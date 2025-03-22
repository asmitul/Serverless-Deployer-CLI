# Serverless Deployer

A CLI tool to simplify and streamline serverless function deployments across multiple providers.

## Features

- One-command deployments to AWS Lambda and Vercel
- Configuration management through YAML files
- Environment variable handling with dotenv support
- Deployment history and rollback capabilities
- Pre/post-deployment hooks

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Initialize a new serverless project
serverless-deployer init

# Deploy to a specific provider
serverless-deployer deploy --provider aws

# List available functions
serverless-deployer list

# Get deployment history
serverless-deployer history

# Rollback to a previous deployment
serverless-deployer rollback --deployment-id <id>
```

## Configuration

Create a `serverless.yml` file in your project root:

```yaml
project: my-awesome-api
provider: aws  # or vercel
functions:
  - name: api-handler
    path: ./src/handler.py
    memory: 128
    timeout: 30
    env_file: .env.production
```

## Providers Supported

- AWS Lambda
- Vercel
- More coming soon! 