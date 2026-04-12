# DSCI 575 Project -- Amazon Product Query Assistant

**Team:** Prabuddha Tamhane (`pat0216`), Ojasv Issar (`ojasv31`)

**Repository:** [https://github.com/UBC-MDS/DSCI_575_project_ojasv31_pat0216](https://github.com/UBC-MDS/DSCI_575_project_ojasv31_pat0216)

## About

A retrieval-based product search system for the **Appliances** category of the [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/) dataset. Given a natural language query (e.g. "energy efficient dishwasher under $500"), the system retrieves relevant products using BM25 keyword search and semantic embedding search, and presents them through a Streamlit web app.

## Dataset

We use the **Appliances** category from the Amazon Reviews 2023 dataset (McAuley Lab, UCSD):

| File | Description |
|------|-------------|
| `Appliances.jsonl.gz` | User reviews -- ratings, review text, timestamps, helpful votes |
| `meta_Appliances.jsonl.gz` | Product metadata -- titles, descriptions, features, price, categories |

**Key fields used for retrieval:**

- **Metadata:** `title`, `description`, `features`, `price`, `average_rating`
- **Reviews:** `text`, `rating`, `verified_purchase`, `helpful_vote`
- **Join key:** `parent_asin`

We download a working subset (~20K reviews) using DuckDB and store it as parquet in `data/processed/`. Raw `.jsonl.gz` files go in `data/raw/` and are not committed.

## Data Processing

1. Stream review and metadata files from the McAuley Lab servers using DuckDB
2. Inspect the first 200 entries in the EDA notebook to understand schema, sample text, and missing values
3. Convert to parquet format locally for fast repeated queries
4. Join reviews with metadata on `parent_asin`
5. Drop rows with missing review text or product title

Preprocessing details and justifications are documented in `notebooks/milestone1_exploration.ipynb`.

## Retrieval Methods

### BM25 (keyword search)
Lexical retrieval using a lightweight in-repo BM25 implementation. Documents are tokenized with lowercasing and basic punctuation removal. Returns top-k results ranked by BM25 score. Implementation in `src/bm25.py`.

Persistence:
- Tokenized corpus and BM25 index are saved to `data/processed/bm25_index.pkl`.

### Semantic Search (embedding-based)
Uses `sentence-transformers` (`all-MiniLM-L6-v2`) when available, with a TF-IDF cosine-similarity fallback in this workspace. Implementation in `src/semantic.py`.

Persistence:
- When sentence-transformers is available, a FAISS index and metadata are saved under `data/processed/semantic_faiss/`.

## Step 4: Qualitative Evaluation

The qualitative evaluation workflow lives in `src/qualitative_eval.py` and writes the step-4 report to `results/milestone1_discussion.md`.

It covers:

- A 10-query set spanning easy, medium, and complex query types
- Top-5 retrieval outputs for both BM25 and semantic search
- Side-by-side comparison for five selected queries
- A short discussion of strengths, weaknesses, and cases that may need reranking or RAG

Run the report generator after your processed corpus is available:

```bash
python -m src.qualitative_eval
```

## Step 5: Web App

The Streamlit app is implemented in `app/app.py`.

Features:

- Search mode selector for BM25, Semantic, and Hybrid retrieval
- Query input box
- Top 3 result display with title, review snippet, rating, and retrieval score
- Thumbs-up / thumbs-down feedback buttons
- Local CSV feedback storage in `data/processed/feedback.csv`

If no processed corpus is found, the app falls back to a small demo corpus so the interface still runs.

## Repository Structure

```
DSCI_575_project_ojasv31_pat0216/
|-- README.md
|-- requirements.txt
|-- .env                       # API keys (not committed)
|
|-- data/
|   |-- raw/                   # downloaded .jsonl.gz (gitignored)
|   |-- processed/             # cleaned parquet files (gitignored)
|
|-- notebooks/
|   |-- milestone1_exploration.ipynb
|
|-- src/
|   |-- bm25.py
|   |-- semantic.py
|   |-- retrieval_metrics.py
|   |-- data_io.py
|   |-- ranking.py
|   |-- feedback.py
|   |-- qualitative_eval.py
|   |-- utils.py
|
|-- results/
|   |-- milestone1_discussion.md
|
|-- app/
    |-- app.py
```

## Setup and Reproduction

### 1. Clone the repository

```bash
git clone https://github.com/UBC-MDS/DSCI_575_project_ojasv31_pat0216.git
cd DSCI_575_project_ojasv31_pat0216
```

### 2. Create environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```
HF_TOKEN=your_huggingface_token_here
```

### 4. Run the EDA notebook

Open and run `notebooks/milestone1_exploration.ipynb` to download and preprocess the data. This will populate `data/processed/` with the cleaned parquet files needed by the retrieval scripts and the app.

### 5. Run the app

```bash
streamlit run app/app.py
```

### 5.1 Build persistent indexes (recommended before running app)

```bash
python -m src.build_indexes
```

This creates:
- `data/processed/bm25_index.pkl`
- `data/processed/semantic_faiss/index.faiss`
- `data/processed/semantic_faiss/metadata.json`

The app automatically loads these persisted indexes when present.

### 6. Generate the Step 4 report

```bash
python -m src.qualitative_eval
```