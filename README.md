# Health Condition Assistant Bot (NOTE: IN DEVELOPMENT -- WIP)

### A chatbot using minimal retrieval augmented generation (RAG) over a dataset of clinical conditions, designed to provide concise information summaries along with source links to verify the reliability of the answers.

Developed initially from the rag-tutorial project at https://github.com/pixegami (Thank you, pixelgami)

## Setup
- Clone this repo:
    -  ```git clone https://github.com/sadieflick/clinical_chat_bot``` in terminal
- Create a local environment within your project:
    -  ```cd clinical_chat_bot```
    - ```python -m venv .venv```
- Activate environment:
    - ```source .venv/bin/activate```
- Install dependencies: 
    - ```pip install -r requirements.txt```
- Follow the instructions to install Ollama: https://github.com/ollama/ollama?tab=readme-ov-file#ollama
- Run Ollama on port 1134:
    - ```ollama run llama3.2```
- Navigate to localhost:1134 in your browser to check that it is running.
- To pull model for embeddings:
    - ```ollama pull llama3.2```
    - ```ollama pull nomic-embed-text```
