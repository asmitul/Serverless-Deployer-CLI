# Installing Serverless Deployer

## Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- For AWS Lambda deployments: AWS CLI configured with appropriate credentials
- For Vercel deployments: Vercel CLI or authentication token

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd serverless-deployer
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Verify installation:
   ```bash
   serverless-deployer --version
   ```

## Environment Setup

### For AWS Lambda Deployments

1. Ensure you have AWS credentials configured:
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_REGION=your-region
   export AWS_LAMBDA_ROLE_ARN=your-lambda-execution-role-arn
   ```

   Or add them to your `.env` file.

### For Vercel Deployments

1. Set up Vercel authentication:
   ```bash
   export VERCEL_TOKEN=your-vercel-token
   export VERCEL_ORG_ID=your-org-id  # Optional
   export VERCEL_PROJECT_ID=your-project-id  # Optional
   ```

   Or add them to your `.env` file.

## Quick Start

1. Initialize a new serverless project:
   ```bash
   serverless-deployer init --name my-project --provider aws
   ```

2. Edit the generated `serverless.yml` file to configure your functions.

3. Deploy your functions:
   ```bash
   serverless-deployer deploy
   ```

See the [README.md](README.md) for more detailed usage instructions. 