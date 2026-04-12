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
2. Convert to parquet format locally for fast repeated queries
3. Join reviews with metadata on `parent_asin`
4. Drop rows with missing review text or product title

Preprocessing details and justifications are documented in `notebooks/milestone1_exploration.ipynb`.

## Retrieval Methods

### BM25 (keyword search)
Lexical retrieval using the `rank_bm25` library. Documents are tokenized with lowercasing and basic punctuation removal. Returns top-k results ranked by BM25 score. Implementation in `src/bm25.py`.

### Semantic Search (embedding-based)
Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to embed documents and queries into a shared vector space. FAISS index for fast similarity search. Implementation in `src/semantic.py`.

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