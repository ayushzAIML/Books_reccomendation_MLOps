# ZenML Integration Guide

## Overview

This project has been enhanced with **ZenML** - a production-grade ML pipeline orchestration framework. The ZenML integration provides:

✅ **Pipeline Orchestration** - Automated artifact and model loading  
✅ **Artifact Tracking** - Automatic versioning and caching of artifacts  
✅ **Step Composition** - Modular, reusable pipeline components  
✅ **Logging & Monitoring** - Built-in observability and debugging  
✅ **Non-Invasive** - Zero changes to your recommendation logic  

---

## Project Structure

```
src/
├── config.py                          # Centralized configuration
├── run_zenml_pipeline.py             # Entry point to run the pipeline
├── pipelines/
│   └── recommender_pipeline.py       # ✅ YOUR EXISTING RECOMMENDATION LOGIC (UNCHANGED)
├── services/                          # ✅ Embedding, search, metadata services (UNCHANGED)
├── api/                               # ✅ FastAPI endpoints (UNCHANGED)
├── zenml_pipelines/
│   ├── __init__.py
│   └── initialization_pipeline.py    # New ZenML pipeline definition
└── steps/
    ├── __init__.py
    ├── load_artifacts.py             # NEW: Load embeddings, metadata, FAISS index
    ├── load_models.py                # NEW: Load bi-encoder and cross-encoder
    ├── load_user_profiles.py         # NEW: Load user preference profiles
    ├── validate_pipeline.py          # NEW: Validate pipeline readiness
    ├── ingest_data.py                # [DEPRECATED] - kept for backward compatibility
    ├── embed_books.py                # [DEPRECATED] - pre-computed embeddings
    ├── build_faiss.py                # [DEPRECATED] - pre-built FAISS index
    ├── train_model.py                # [DEPRECATED] - pre-trained models
    ├── evaluate.py                   # [DEPRECATED] - validation via validate_pipeline
    └── preprocess_data.py            # [DEPRECATED] - pre-processed data

data/
├── processed/
│   └── books_metadata_with_genre.csv  # Metadata with ISBN, title, genre, description
├── embeddings/
│   ├── embeddings.npy                # Pre-computed embeddings (N, 384)
│   └── isbn_list.csv                 # ISBN list in same order as embeddings
├── faiss/
│   └── faiss_index.bin               # Pre-built FAISS index
├── user/
│   └── cleaned_ratings.csv           # User ratings for profile building
└── userss/
    └── user_profiles.json            # Persistent user profiles and embeddings
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify All Required Files Exist

```
✓ /data/processed/books_metadata_with_genre.csv  - Book metadata
✓ /data/embeddings/embeddings.npy               - Embeddings (pre-computed)
✓ /data/embeddings/isbn_list.csv                - ISBN list
✓ /data/faiss/faiss_index.bin                   - FAISS index (pre-built)
```

### 3. Initialize ZenML

```bash
cd /home/ayushz/Projects/Books_recommendation_END_TO_END
zenml init
```

### 4. Run the Pipeline

```bash
python src/run_zenml_pipeline.py
```

Expected output:
```
================================================================================
🚀 Starting ZenML Books Recommendation Pipeline
================================================================================

📋 Executing pipeline...

✓ Found Metadata CSV
✓ Found Embeddings NPY
✓ Found FAISS Index
✓ Found ISBN List
📖 Loading metadata...
✓ Loaded 10000 books from metadata
...
✅ Pipeline executed successfully!
================================================================================
```

---

## Pipeline Architecture

### Initialization Pipeline (`books_recommendation_initialization`)

The pipeline loads and validates all components in the correct order:

```
┌─────────────────────────────────────────────┐
│ books_recommendation_initialization         │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌────────┐ ┌────────┐ ┌──────────────┐
    │ Load   │ │ Load   │ │ Load User    │
    │Artifacts│ │ Models │ │ Profiles     │
    └────────┘ └────────┘ └──────────────┘
        │           │           │
        └───────────┼───────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ Validate Pipeline│
            └──────────────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ Pipeline Ready   │
            └──────────────────┘
```

### Individual Steps

#### 1. **load_artifacts** (`src/steps/load_artifacts.py`)
- Loads metadata, embeddings, FAISS index, and ISBN mappings
- Validates all files exist
- Normalizes embeddings for cosine similarity
- Returns: DataFrame, embeddings, FAISS index, ISBN list, metadata dict

#### 2. **load_models** (`src/steps/load_models.py`)
- Loads SentenceTransformer bi-encoder (for query encoding)
- Loads CrossEncoder (for semantic relevance scoring)
- Models downloaded from HuggingFace (cached locally)
- Returns: bi_encoder, cross_encoder

#### 3. **load_user_profiles** (`src/steps/load_user_profiles.py`)
- Loads existing user profiles from JSON
- Creates empty profiles dict if file doesn't exist
- Returns: user_profiles dictionary

#### 4. **validate_pipeline** (`src/steps/validate_pipeline.py`)
- Validates all artifacts are loaded correctly
- Checks data consistency
- Logs pipeline readiness status
- Returns: True if valid, raises exception if invalid

---

## Configuration

All settings are centralized in `src/config.py`:

```python
# Data paths (auto-discovered)
META_CSV = ".../books_metadata_with_genre.csv"
EMB_NPY = ".../embeddings.npy"
FAISS_INDEX = ".../faiss_index.bin"
ISBN_LIST = ".../isbn_list.csv"
RATINGS_CSV = ".../cleaned_ratings.csv"
USER_PROFILE_PATH = ".../user_profiles.json"

# ML Models
BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Recommendation weights (must sum to 1.0)
W_CE = 0.55         # Cross-encoder semantic relevance
W_GENRE = 0.15      # Genre boost
W_USER = 0.15       # Long-term personalization
W_SESSION = 0.15    # Short-term session mood
```

---

## Your Recommendation Logic (UNCHANGED ✅)

Your existing recommendation system at `src/pipelines/recommender_pipeline.py` is **100% untouched**. The ZenML integration only handles:

- Loading artifacts
- Loading models
- Managing user profiles
- Validating components

**Your code still does:**
- ✅ Query encoding with bi-encoder
- ✅ FAISS fast nearest neighbor search
- ✅ Cross-encoder re-ranking
- ✅ Genre boosting
- ✅ User profile personalization
- ✅ Session-based mood tracking
- ✅ Feedback ingestion and profile updates

---

## Data Flow

### Data Preparation Phase (Before Pipeline)

```
Raw Data
   ├── BX-Book-Ratings.csv
   ├── cleaned_books.csv
   └── User ratings
        │
        ▼
   Preprocessing Scripts (src/scripts/)
        │
        ├─► Genre inference
        ├─► Dataset merging
        └─► Description enrichment
        │
        ▼
   Processed Data
        ├── books_metadata_with_genre.csv ─────┐
        │                                       │
        ├── cleaned_ratings.csv ────────────┐  │
        └── Embeddings (pre-computed)       │  │
```

### Pipeline Phase (ZenML Orchestration)

```
Pre-computed Artifacts
   ├── embeddings.npy
   ├── isbn_list.csv
   ├── faiss_index.bin
   └── books_metadata_with_genre.csv
        │
        ▼
   Load Artifacts Step
        │
        ├─► Validate files exist
        ├─► Normalize embeddings
        ├─► Build ISBN→index mapping
        └─► Load FAISS index
        │
        ▼
   Load Models Step
        │
        ├─► Download/cache bi-encoder
        └─► Download/cache cross-encoder
        │
        ▼
   Load User Profiles Step
        │
        └─► Load/initialize user_profiles.json
        │
        ▼
   Validate Pipeline Step
        │
        ├─► Check artifacts consistency
        ├─► Verify models loaded
        └─► Report readiness status
        │
        ▼
   ✅ Pipeline Ready for Serving
```

### Runtime Phase (Your Recommendation Logic)

```
User Query
   │
   ▼
recommender_pipeline.py
   ├─► Encode query (bi-encoder)
   ├─► FAISS search (top 50)
   ├─► Cross-encoder re-rank
   ├─► Genre boost
   ├─► User profile personalization
   ├─► Session mood adjustment
   └─► Return top 10
   │
   ▼
FastAPI Endpoints (api/main.py)
   │
   ▼
Client/Frontend
```

---

## Integration with Existing Code

### For Your API (`src/api/main.py`)

You can optionally integrate the pipeline:

```python
from src.zenml_pipelines import books_recommendation_initialization
from src.pipelines.recommender_pipeline import recommend

# On startup:
@app.on_event("startup")
async def startup():
    # Optionally validate pipeline on startup
    books_recommendation_initialization()
    
@app.post("/recommend")
async def get_recommendations(request: RecommendRequest):
    # Your existing recommendation logic
    results = recommend(
        user_id=request.user_id,
        query=request.query,
        preferred_genre=request.genre
    )
    return {"recommendations": results}
```

### For Your CLI (`recommender_pipeline.py`)

No changes needed! Your CLI continues to work as-is. The ZenML pipeline runs independently.

---

## ZenML Features Used

### 1. **Steps** - Modular pipeline components
Each step is a unit of execution that:
- Has typed inputs and outputs
- Logs automatically
- Caches results
- Can be versioned

### 2. **Pipeline** - Orchestrates steps
Defines the DAG (Directed Acyclic Graph) of execution and manages:
- Artifact passing between steps
- Execution order
- Error handling

### 3. **Logging** - Built-in observability
Each step logs:
- Input validation
- Processing status
- Output summary
- Errors with full context

### 4. **Artifact Tracking** - Automatic versioning
All artifacts are:
- Versioned automatically
- Tracked with metadata
- Retrievable from ZenML store

---

## Troubleshooting

### Issue: "Metadata CSV must contain 'isbn' column"
**Solution:** Verify your metadata CSV has an 'isbn' column:
```bash
head -1 /data/processed/books_metadata_with_genre.csv
```

### Issue: FAISS index not found
**Solution:** Build the FAISS index separately (requires embeddings):
```bash
# See your data preparation scripts in src/scripts/
```

### Issue: Models taking too long to download
**Solution:** Models are cached after first download. Subsequent runs use cache.

### Issue: User profiles file corrupted
**Solution:** Delete it and let the pipeline reinitialize:
```bash
rm /data/userss/user_profiles.json
# Pipeline will create a fresh file
```

---

## Best Practices

1. **Keep artifacts pre-computed** - Don't regenerate embeddings/FAISS in production
2. **Run validation on startup** - Catch issues early
3. **Monitor artifact versions** - Track which embeddings/index versions are in use
4. **Backup user profiles** - JSON profiles are valuable
5. **Use centralized config** - All paths in `src/config.py`

---

## What's NOT Changed

❌ Your recommendation algorithm - **UNCHANGED**  
❌ Your CLI interaction logic - **UNCHANGED**  
❌ Your profile update mechanisms - **UNCHANGED**  
❌ Your FAISS search implementation - **UNCHANGED**  
❌ Your API structure - **UNCHANGED**  

---

## Next Steps

1. ✅ Review this guide
2. ✅ Run `python src/run_zenml_pipeline.py`
3. ✅ Verify all components load successfully
4. ✅ Optionally integrate pipeline validation into your API startup
5. ✅ Deploy with confidence!

---

## Support

For ZenML documentation: https://docs.zenml.io/  
For issues specific to this integration, check logs in:
```
.zenml/  # ZenML configuration and metadata store
```

---

**Happy recommending! 📚✨**
