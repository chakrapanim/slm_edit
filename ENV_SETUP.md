# Environment Setup for LLM Evaluation

The evaluation script now supports loading API credentials from a `.env` file. This allows you to securely store your API keys without hardcoding them.

## Setup

### 1. Create a `.env` file

Create a `.env` file in the project root directory with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### 2. Alternative: Regular OpenAI

If you prefer to use regular OpenAI instead of Azure OpenAI:

```env
# Regular OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
```

## Required Environment Variables

### For Azure OpenAI:
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
- `AZURE_OPENAI_DEPLOYMENT_NAME` - The name of your model deployment
- `AZURE_OPENAI_API_VERSION` - API version (optional, defaults to `2024-02-15-preview`)

### For Regular OpenAI:
- `OPENAI_API_KEY` - Your OpenAI API key

## How It Works

1. The script automatically loads the `.env` file using `python-dotenv`
2. It checks for Azure OpenAI credentials first
3. If Azure credentials are found, it uses Azure OpenAI
4. If not, it falls back to regular OpenAI
5. If neither is found, LLM evaluation is skipped

## Example .env File

```env
# Azure OpenAI (recommended)
AZURE_OPENAI_API_KEY=abc123def456...
AZURE_OPENAI_ENDPOINT=https://my-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Security Note

- **Never commit your `.env` file to version control**
- The `.env` file is already in `.gitignore` (or should be)
- Keep your API keys secure and private

## Running the Evaluation

Once your `.env` file is set up, simply run:

```bash
python main_evaluation_expanded.py
```

The script will automatically:
1. Load credentials from `.env`
2. Detect whether to use Azure OpenAI or regular OpenAI
3. Run LLM evaluation if credentials are available
4. Continue without LLM evaluation if credentials are missing
