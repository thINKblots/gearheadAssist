# GearHead Assistant

A Streamlit-powered chat interface for mobile equipment diagnostics and troubleshooting, using a custom Ollama model based on llama3.1:8b.

## Features

- Interactive chat interface for equipment diagnostics
- Streaming responses for real-time feedback
- RAG (Retrieval Augmented Generation) with Pinecone vector database
- Clickable citations linking to source PDF documents
- Chat history management
- Example prompts for common questions
- Specialized knowledge for:
  - Mini excavators
  - Skid steer loaders
  - Boom lifts
  - Scissor lifts
  - Counterbalance forklifts
  - Variable reach forklifts
  - Other mobile equipment

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- The gearhead8b model created in Ollama

## Setup

### 1. Install Ollama

If you haven't already, install Ollama from [https://ollama.ai/](https://ollama.ai/)

### 2. Create the Custom Model

Create the gearhead8b model using the provided Modelfile:

```bash
ollama create gearhead8b -f Modelfile
```

Verify the model was created:

```bash
ollama list
```

You should see `gearhead8b` in the list of available models.

### 3. Install Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or install them individually:

```bash
pip install streamlit ollama
```

### 4. Configure PDF Citations (Optional)

To enable clickable PDF citations, set the base URL where your PDFs are hosted:

```bash
# Add to .env file
BASE_PDF_URL=https://your-pdf-hosting-url.com/pdfs
```

See [PDF_HOSTING_GUIDE.md](PDF_HOSTING_GUIDE.md) for detailed instructions on hosting PDFs.

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

1. Type your question about mobile equipment diagnostics in the chat input
2. Press Enter or click the send button
3. Watch as the AI assistant provides real-time responses
4. Use the sidebar to:
   - Check model status
   - Clear chat history
   - View example questions
   - Click example questions to quickly test the assistant

## Example Questions

- "My mini excavator won't start. What should I check?"
- "How do I diagnose hydraulic issues on a skid steer?"
- "What are common causes of a scissor lift not raising?"
- "My forklift is losing power. What could be wrong?"

## Model Configuration

The gearhead8b model is configured with:
- Base model: llama3.1:8b
- Temperature: 0.5 (balanced creativity)
- Context window: 8192 tokens
- Specialized system prompt for mobile equipment diagnostics

See [Modelfile](Modelfile) for complete configuration details.

## Deploying to Streamlit Cloud

**Important:** Streamlit Community Cloud doesn't support running Ollama directly. You need to run Ollama on a separate server.

### Quick Deployment Steps:

1. **Set up Ollama on a server** (see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions)
   - Option A: Use a cloud VM ($5-12/month)
   - Option B: Run on your local machine (for testing only)

2. **Configure environment variable:**
   - In Streamlit Cloud settings → Secrets, add:
   ```toml
   OLLAMA_HOST = "https://your-ollama-server.com"
   ```

3. **Deploy to Streamlit Cloud:**
   - Push code to GitHub
   - Connect repo at [share.streamlit.io](https://share.streamlit.io)
   - App will connect to your Ollama server

For complete deployment instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## Troubleshooting

### Model Not Found

If you see "Model 'gearhead8b' not found":
1. Ensure Ollama is running
2. Create the model: `ollama create gearhead8b -f Modelfile`
3. Restart the Streamlit app

### Connection Error

If you can't connect to Ollama:
1. Check if Ollama is running: `ollama list`
2. Restart Ollama service
3. Verify Ollama is accessible at default port (11434)

### Performance Issues

If responses are slow:
- The first response may take longer as the model loads
- Subsequent responses should be faster
- Consider using a machine with more RAM for better performance

## License

This project uses the llama3.1:8b model, which has its own license terms. Please review Ollama's and Meta's licensing for commercial use.
