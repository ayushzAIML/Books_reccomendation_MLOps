# Book Recommendation System (Hybrid Recommender)

A **Hybrid Book Recommendation System** that combines **collaborative filtering** (user-book interactions) and **content-based recommendation** using **text embeddings from book descriptions**. The system is production-ready with **MLOps** practices using **ZenML, MLflow, and FastAPI**.

---

## 🚀 Project Goal

Recommend books similar to what users like by:

* Understanding **what books are about** (description embeddings)
* Learning **which books users interact with** (ratings data)
* Combining these to give **smart, personalized recommendations**

---

## 📂 Project Structure

```
BOOKS_RECOMMENDER/
│
├── data/
│   ├── raw/                       # original CSVs
│   │   ├── BX-Book-Ratings.csv
│   │   └── cleaned_books.csv
│   ├── processed/                 # after preprocessing
│   └── embeddings/                # book text embeddings saved here
│
├── notebooks/
│   ├── EDA.ipynb
│   └── Data_Prep.ipynb
│
├── src/
│   ├── steps/                     # ZenML steps (your existing step files)
│   │   ├── ingest_data.py
│   │   ├── preprocess_data.py
│   │   ├── embed_books.py
│   │   ├── build_interaction_matrix.py
│   │   ├── train_model.py
│   │   ├── evaluate.py
│   │   └── register_model.py
│   │
│   ├── pipelines/
│   │   └── recommender_pipeline.py
│   │
│   ├── models/                    # model utils OR saved artifacts
│   │
│   └── scripts/                   # One-time utility scripts
│       ├── dataset_merge.py
│       └── desc_genre.py
│
├── readme.md
└── requirements.txt

```

---

## 🔧 Hybrid Model Overview

### 1) **Content-Based Embeddings**

* Convert **book descriptions + genres** into **vector embeddings** using a Sentence Transformer.
* Books with similar content → Close in vector space.

### 2) **Collaborative Filtering (Matrix Factorization)**

* Learn patterns from **user-book ratings**.
* Discovers "people who like X also like Y" behavior.

### 3) **Hybrid Scoring**

```
Final_Score = α * Collaborative_Score + (1-α) * Content_Similarity_Score
```

* This balances **personal preference** + **book meaning**

---

## 🧱 ZenML Pipeline Flow

```
ingest_data → preprocess_data → build_interaction_matrix → embed_books → train_model → evaluate → register_model
```

### Why ZenML?

* Ensures workflows are **reproducible**, **versioned**, and **organized**
* Easy to retrain models automatically

---

## 📊 Experiment Tracking (MLflow)

MLflow stores:

* Model performance metrics
* Model versions
* Parameters used in training

So we can **compare** experiments and keep only the best model.

---

## 🌐 Model Deployment (FastAPI)

After training, the model is served via API.

### Endpoints:

```
GET /recommend/{user_id}
```

Returns top recommended books.

```
GET /similar/{book_id}
```

Returns books similar to a given book.

---

## 🏗️ How to Run

### 1) Set up environment

```
pip install -r requirements.txt
```

### 2) Run the ZenML pipeline

```
zenml up
python pipelines/recommender_pipeline.py
```

### 3) Start MLflow UI

```
mlflow ui
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 4) Start API

```
uvicorn app:app --reload
```

---

## ✅ Next Steps

* Add implicit feedback learning (clicks / views)
* Tune α to optimize hybrid performance
* Deploy API to cloud (Render / AWS / Railway)

---

## ⭐ Outcome

This architecture ensures:

* **Better accuracy** than pure collaborative filtering
* **Generalizes to new books** via content embeddings
* Fully **MLOps production aligned** (top 1% ready)

---

Feel free to ask for:

* API code
* Pipeline improvements
* UI for frontend bookshelf app 📚✨
