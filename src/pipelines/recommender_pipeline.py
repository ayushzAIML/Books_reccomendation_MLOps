#!/usr/bin/env python3
"""
S-Tier Recommender — Single-file production-ready script (CLI)
Features:
- FAISS retrieval (fast ANN)
- Bi-encoder (SentenceTransformer) for query encoding
- Cross-encoder re-ranking (CrossEncoder)
- Genre-aware boosting
- Long-term user profiles from ratings (persistent JSON)
- Short-term session (mood) vector (in-memory per CLI session)
- Thumbs up / thumbs down weighting and ratings ingestion
- Deduplication of editions
- Safe ISBN normalization and robust matching

Place this file at:
  /home/ayushz/Projects/Books_recommendation_END_TO_END/src/recommend_s_tier.py

Run:
  python3 recommend_s_tier.py
"""

import os
import json
import time
import numpy as np
import pandas as pd
import faiss
from typing import List, Optional
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity


# CONFIG (Edit if needed)

META_CSV = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/processed/books_metadata_with_genre.csv"
EMB_NPY = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/embeddings.npy"
FAISS_INDEX = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/faiss/faiss_index.bin"
ISBN_LIST = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/embeddings/isbn_list.csv"
RATINGS_CSV = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/user/cleaned_ratings.csv"  # should exist or be created
USER_PROFILE_PATH = "/home/ayushz/Projects/Books_recommendation_END_TO_END/data/userss/user_profiles.json"

# Models (you can change to stronger ones later)
BI_ENCODER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Blending weights (tuneable)
W_CE = 0.55     # cross-encoder weight (semantic relevance)
W_GENRE = 0.15  # genre boost weight
W_USER = 0.15   # long-term personalization weight
W_SESSION = 0.15  # short-term session (mood) weight

# Operational sizes
RETRIEVE_TOP = 50
FINAL_K = 10

# Session memory limits
SESSION_HISTORY_LIMIT = 12  # keep last N interacted ISBNs in session


# Helpers: ISBN normalization

def norm_isbn(isbn):
    if pd.isna(isbn):
        return ""
    s = str(isbn)
    s = s.strip().replace("-", "").replace(" ", "").lower()
    return s


# Load data & artifacts

print("Loading metadata...")
df = pd.read_csv(META_CSV, dtype=str).fillna("")
df.columns = [c.lower() for c in df.columns]  # ensure lowercase columns
if "isbn" not in df.columns:
    raise ValueError("Metadata CSV must contain 'isbn' column.")

# normalize metadata ISBNs
df["isbn"] = df["isbn"].apply(norm_isbn)

print("Loading isbn list...")
isbn_list_df = pd.read_csv(ISBN_LIST, dtype=str).fillna("")
isbn_list = [norm_isbn(x) for x in isbn_list_df.iloc[:, 0].tolist()]

# build mapping ISBN -> embedding index using normalized form
isbn_to_idx = {isbn: i for i, isbn in enumerate(isbn_list)}

print("Loading embeddings (npy)...")
embeddings = np.load(EMB_NPY).astype("float32")  # shape (N, D)

# normalized embeddings copy for fast dot (cosine) computations
embeddings_norm = normalize(embeddings.copy(), axis=1)

print("Loading FAISS index...")
faiss_index = faiss.read_index(FAISS_INDEX)


# Load / prepare models

print("Loading bi-encoder model...")
bi_encoder = SentenceTransformer(BI_ENCODER_MODEL)

print("Loading cross-encoder model...")
cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)


# User profiles persistence

os.makedirs(os.path.dirname(USER_PROFILE_PATH), exist_ok=True)
if not os.path.exists(USER_PROFILE_PATH):
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump({}, f)

with open(USER_PROFILE_PATH, "r") as f:
    try:
        user_profiles = json.load(f)
    except Exception:
        user_profiles = {}

def save_user_profiles():
    with open(USER_PROFILE_PATH, "w") as f:
        json.dump(user_profiles, f)

def get_user_vector(user_id: str) -> Optional[np.ndarray]:
    rec = user_profiles.get(user_id)
    if not rec or not rec.get("vector"):
        return None
    vec = np.array(rec["vector"], dtype="float32")
    norm = np.linalg.norm(vec)
    if norm == 0:
        return None
    return vec / norm


# Ratings ingestion (for building initial profiles)

def ingest_ratings_and_build_profiles(ratings_csv: str = RATINGS_CSV, smoothing: float = 0.6):
    """
    Reads ratings CSV with columns: user_id,isbn,rating (rating numeric, 1-5 typical).
    Builds per-user profile vectors and stores them in user_profiles (persistent json).
    """
    if not os.path.exists(ratings_csv):
        print("Ratings file not found, skipping initial profile building.")
        return

    rdf = pd.read_csv(ratings_csv, dtype=str).fillna("")
    if "user_id" not in rdf.columns or "isbn" not in rdf.columns or "rating" not in rdf.columns:
        print("Ratings CSV must have columns: user_id,isbn,rating")
        return

    # normalize and convert rating
    rdf["isbn"] = rdf["isbn"].apply(norm_isbn)
    rdf["rating"] = pd.to_numeric(rdf["rating"], errors="coerce").fillna(3.0)

    grouped = rdf.groupby("user_id")
    count = 0
    for uid, grp in grouped:
        vecs = []
        weights = []
        for _, row in grp.iterrows():
            isbn = row["isbn"]
            rating = float(row["rating"])
            idx = isbn_to_idx.get(isbn)
            if idx is None:
                continue
            emb = embeddings[idx]
            # convert rating (1-5) -> weight (-1 .. +1)
            w = (rating - 3.0) / 2.0
            vecs.append(emb * w)
            weights.append(abs(w))
        if not vecs:
            continue
        # build weighted average; if all negative (push-away), still produce vector
        vec = np.sum(np.vstack(vecs), axis=0)
        if np.linalg.norm(vec) == 0:
            continue
        vec = vec / np.linalg.norm(vec)
        # smooth with existing profile if present
        if uid in user_profiles and user_profiles[uid].get("vector"):
            old = np.array(user_profiles[uid]["vector"], dtype="float32")
            if np.linalg.norm(old) > 0:
                vec = smoothing * old + (1 - smoothing) * vec
                vec = vec / (np.linalg.norm(vec) + 1e-9)
        user_profiles[uid] = {"vector": vec.tolist(), "liked_isbns": []}
        count += 1

    save_user_profiles()
    print(f"Ingested ratings and built {count} user profiles.")

# Optionally build initial profiles
ingest_ratings_and_build_profiles()


# Session state (in-memory per CLI run)

session_history: List[str] = []  # store normalized ISBNs of recent interactions within this run

def add_session_isbn(isbn: str):
    n = norm_isbn(isbn)
    if not n:
        return
    session_history.append(n)
    # keep last N
    if len(session_history) > SESSION_HISTORY_LIMIT:
        session_history.pop(0)

def get_session_vector() -> Optional[np.ndarray]:
    valid = [isbn_to_idx.get(x) for x in session_history if isbn_to_idx.get(x) is not None]
    if not valid:
        return None
    vecs = embeddings_norm[valid]
    svec = np.mean(vecs, axis=0)
    norm = np.linalg.norm(svec)
    if norm == 0:
        return None
    return svec / norm


"""Update profile on user action (thumbs up/down or rating append)"""

def update_profile_from_feedback(user_id: str, isbn: str, rating: float = 5.0, smoothing: float = 0.6):
    """
    rating: 1-5 scale. >=4 considered positive, <=2 negative.
    Applies an immediate update by combining new weighted vector into existing user profile.
    """
    isbn_n = norm_isbn(isbn)
    idx = isbn_to_idx.get(isbn_n)
    if idx is None:
        print("ISBN not in embeddings map, cannot update profile:", isbn)
        return False

    item_vec = embeddings_norm[idx]  # normalized
    # rating -> weight: -1 .. +1
    w = (rating - 3.0) / 2.0

    # If negative weight, treat as moving away: subtract w*vec (w negative)
    new_component = item_vec * w

    # load old profile
    old_vec = get_user_vector(user_id)
    if old_vec is None:
        # create new profile from this item (if rating positive) or skip if negative (cold start)
        if w <= 0:
            # for negative feedback on cold-start: create small negative vector? better to skip
            print("Negative feedback on cold user — skip creating profile.")
            return False
        profile_vec = new_component
    else:
        profile_vec = (1 - smoothing) * old_vec + smoothing * new_component

    # normalize and store
    if np.linalg.norm(profile_vec) == 0:
        print("Profile update led to zero vector; skipping.")
        return False
    profile_vec = profile_vec / np.linalg.norm(profile_vec)

    # update liked_isbns list (for record)
    record = user_profiles.get(user_id, {"vector": None, "liked_isbns": []})
    liked = record.get("liked_isbns", [])
    if rating >= 4:
        # positive: add to front
        liked = [isbn_n] + [x for x in liked if x != isbn_n]
    else:
        # negative: remove if present
        liked = [x for x in liked if x != isbn_n]

    user_profiles[user_id] = {"vector": profile_vec.tolist(), "liked_isbns": liked}
    save_user_profiles()
    print(f"Updated profile for user {user_id} (rating={rating}).")
    return True


"""Genre boost util"""

def genre_boost_score(preferred_genre: Optional[str], book_genre: str) -> float:
    if not preferred_genre or not isinstance(book_genre, str) or not book_genre:
        return 0.0
    return 0.35 if preferred_genre.lower() in book_genre.lower() else 0.0


"""Deduplication util"""

def dedupe_results(results: List[dict]) -> List[dict]:
    seen = set()
    out = []
    for r in results:
        key = (r["title"].lower(), r["author"].lower())
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


"""Core recommend function"""

def recommend(user_id: str, query: str, preferred_genre: Optional[str] = None,
              retrieve_top: int = RETRIEVE_TOP, final_k: int = FINAL_K):
    # 1) embed query
    q_vec = bi_encoder.encode([query]).astype("float32")
    q_norm = normalize(q_vec, axis=1).astype("float32")

    # 2) FAISS search (use normalized vector if index uses inner product on normalized vectors)
    distances, indices = faiss_index.search(q_norm, retrieve_top)
    candidate_idxs = indices[0].tolist()

    # Build candidate block
    candidates = df.iloc[candidate_idxs].copy().reset_index(drop=True)
    candidates["__emb_idx"] = candidate_idxs

    # 3) Cross-encoder rerank
    pairs = []
    for _, row in candidates.iterrows():
        title = row.get("title", "")
        desc = row.get("description", "")
        text = f"{title} {desc}"
        pairs.append([query, str(text)])
    ce_scores = cross_encoder.predict(pairs)
    candidates["ce_score"] = ce_scores

    # 4) Genre score
    if preferred_genre:
        candidates["genre_score"] = candidates["genre"].apply(lambda g: genre_boost_score(preferred_genre, g))
    else:
        candidates["genre_score"] = 0.0

    # 5) User long-term score
    user_vec = get_user_vector(user_id)
    if user_vec is not None:
        cand_embs_norm = embeddings_norm[candidate_idxs]  # shape (retrieve_top, D)
        user_scores = np.dot(cand_embs_norm, user_vec)  # cosine similarity
        candidates["user_score"] = user_scores
    else:
        candidates["user_score"] = 0.0

    # 6) Session short-term score
    session_vec = get_session_vector()
    if session_vec is not None:
        cand_embs_norm = embeddings_norm[candidate_idxs]
        session_scores = np.dot(cand_embs_norm, session_vec)
        candidates["session_score"] = session_scores
    else:
        candidates["session_score"] = 0.0

    # 7) Final blended score
    candidates["final_score"] = (
        W_CE * candidates["ce_score"].astype(float).values +
        W_GENRE * candidates["genre_score"].astype(float).values +
        W_USER * candidates["user_score"].astype(float).values +
        W_SESSION * candidates["session_score"].astype(float).values
    )

    # 8) Sort and prepare results
    candidates = candidates.sort_values("final_score", ascending=False).reset_index(drop=True)

    results = []
    for _, row in candidates.iterrows():
        results.append({
            "title": row.get("title", ""),
            "author": row.get("author", ""),
            "genre": row.get("genre", "Unknown"),
            "isbn": str(row.get("isbn", "")),
            "score": float(row.get("final_score", 0.0)),
            "emb_idx": int(row.get("__emb_idx"))
        })
    results = dedupe_results(results)
    return results[:final_k]


"""CLI loop with session & feedback"""

def cli_loop():
    print("\n=== S-Tier Recommender CLI ===\n")
    user_id = input("Enter your user id (creates profile if new): ").strip()
    if user_id == "":
        print("User ID required. Exiting.")
        return

    while True:
        print("\nOptions:\n  1) Recommend\n  2) Rate historical page (import ratings CSV)\n  3) Manual: thumbs up/down a shown ISBN\n  4) Show user profile summary\n  5) Clear session history\n  6) Exit")
        choice = input("Choose (1-6): ").strip()

        if choice == "1":
            query = input("Describe a book / mood / topic: ").strip()
            if not query:
                print("Query required.")
                continue
            preferred_genre = input("Optional preferred genre (press Enter to skip): ").strip() or None

            print("\nSearching... (FAISS + cross-encoder running)")
            results = recommend(user_id, query, preferred_genre)

            if not results:
                print("No results found.")
                continue

            print("\nTop recommendations:")
            for i, r in enumerate(results, 1):
                print(f"#{i} (score: {r['score']:.3f})")
                print(f"  {r['title']} — {r['author']}")
                print(f"  Genre: {r['genre']}  ISBN: {r['isbn']}")
                print("-" * 40)

            # Ask for interactions in this session: click / like / dislike
            click_input = input("\nEnter numbers you clicked/viewed (comma-separated), or press Enter: ").strip()
            clicked_isbns = []
            if click_input:
                try:
                    nums = [int(x.strip()) for x in click_input.split(",") if x.strip()]
                    for n in nums:
                        if 1 <= n <= len(results):
                            clicked_isbns.append(results[n-1]["isbn"])
                            add_session_isbn(results[n-1]["isbn"])
                except:
                    print("Invalid input, skipping clicks.")

            like_input = input("Enter numbers you LIKED (thumbs up) (comma-separated), or press Enter: ").strip()
            if like_input:
                try:
                    likes = [int(x.strip()) for x in like_input.split(",") if x.strip()]
                    for n in likes:
                        if 1 <= n <= len(results):
                            isbn = results[n-1]["isbn"]
                            # update long-term profile with positive rating=5
                            update_profile_from_feedback(user_id, isbn, rating=5.0, smoothing=0.6)
                            add_session_isbn(isbn)
                    print("Thanks — your likes updated your long-term profile.")
                except Exception as e:
                    print("Failed processing likes:", e)

            dislike_input = input("Enter numbers you DISLIKED (thumbs down) (comma-separated), or press Enter: ").strip()
            if dislike_input:
                try:
                    dislikes = [int(x.strip()) for x in dislike_input.split(",") if x.strip()]
                    for n in dislikes:
                        if 1 <= n <= len(results):
                            isbn = results[n-1]["isbn"]
                            # update profile with negative rating=1
                            update_profile_from_feedback(user_id, isbn, rating=1.0, smoothing=0.6)
                    print("Thanks — your dislikes updated your long-term profile.")
                except Exception as e:
                    print("Failed processing dislikes:", e)

        elif choice == "2":
            # Re-ingest ratings CSV and rebuild profiles
            print("Rebuilding user profiles from ratings CSV (this may take time)...")
            ingest_ratings_and_build_profiles()
            print("Done.")

        elif choice == "3":
            # manual thumbs based on ISBN
            isbn = input("Enter ISBN (any format): ").strip()
            isbn_n = norm_isbn(isbn)
            if not isbn_n:
                print("Invalid ISBN.")
                continue
            r = input("Thumbs up (u) or thumbs down (d)? ").strip().lower()
            if r == "u":
                update_profile_from_feedback(user_id, isbn_n, rating=5.0, smoothing=0.6)
                add_session_isbn(isbn_n)
            elif r == "d":
                update_profile_from_feedback(user_id, isbn_n, rating=1.0, smoothing=0.6)
            else:
                print("Unknown input.")

        elif choice == "4":
            # show user profile summary
            prof = user_profiles.get(user_id)
            if not prof:
                print("No profile for user yet.")
            else:
                vec = np.array(prof["vector"], dtype="float32")
                liked = prof.get("liked_isbns", [])
                print(f"User '{user_id}' profile vector norm: {np.linalg.norm(vec):.4f}")
                print(f"Liked ISBNs (top {len(liked)}): {liked[:10]}")

        elif choice == "5":
            session_history.clear()
            print("Session history cleared.")

        elif choice == "6":
            print("Exiting. Goodbye.")
            break

        else:
            print("Unknown option. Choose 1-6.")

"""
Entrypoint
"""

if __name__ == "__main__":
    cli_loop()
