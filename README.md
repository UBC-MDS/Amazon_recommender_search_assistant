# DSCI_575_project_ojasv31_pat0216

This repository is structured for iterative milestone-based development of an information retrieval project (BM25, semantic retrieval, evaluation, and app integration).

## Project Structure

```text
YOUR-PROJECT/
|
|-- README.md
|-- requirements.txt
|-- .env
|
|-- data/
|   |-- raw/
|   `-- processed/
|
|-- notebooks/
|   |-- milestone1_exploration.ipynb
|   `-- <other notebooks>
|
|-- src/
|   |-- bm25.py
|   |-- semantic.py
|   |-- retrieval_metrics.py
|   `-- <other scripts>
|
|-- results/
|   `-- milestone1_discussion.md
|
`-- app/
	`-- app.py
```

## Folder and File Purpose

### `README.md`
Primary documentation for the project. Keep this updated as the project evolves so collaborators can quickly understand setup, workflow, and milestone status.

### `requirements.txt`
Tracks Python package dependencies used by scripts, notebooks, and the app. Update this file whenever new libraries are added.

### `.env`
Stores environment variables and secrets (API keys, tokens, private URLs). This file should never be committed to source control.

### `data/raw/`
Holds downloaded source datasets (for example `.jsonl.gz` files). Data here is treated as immutable input and should be excluded from git.

### `data/processed/`
Contains cleaned, transformed, chunked, and indexed data artifacts generated from `data/raw/`.

### `notebooks/`
Contains exploratory and milestone-specific notebooks. Use these for analysis, quick experiments, and visual checks before productionizing logic into `src/`.

### `src/`
Core Python modules for retrieval and evaluation logic:
- `bm25.py`: lexical retrieval pipeline.
- `semantic.py`: embedding-based or vector retrieval pipeline.
- `retrieval_metrics.py`: evaluation metrics (precision, recall, MAP, nDCG, etc.).

### `results/`
Stores milestone writeups, experiment comparisons, and result interpretation.

### `app/`
Application entrypoint for demos or deployment. Keep one primary app file and update it each milestone.

## Suggested Workflow

1. Put new source data into `data/raw/`.
2. Process data into reusable artifacts in `data/processed/`.
3. Explore methods in `notebooks/`.
4. Move stable logic into `src/` modules.
5. Evaluate and summarize findings in `results/`.
6. Integrate latest functionality in `app/app.py`.

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add environment variables to `.env`.
4. Start development in `notebooks/` and `src/`.

## Notes

- Keep `data/raw/` and `.env` out of git.
- Favor reproducible scripts in `src/` over notebook-only logic.
- Document milestone assumptions and decisions in `results/`.