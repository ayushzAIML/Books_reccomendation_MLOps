<!-- suggested api deployment file structure -->
project/
│
├── src/
│   ├── api/                          # FastAPI application
│   │   ├── main.py
│   │   ├── routers/
│   │   │   └── recommend.py
│   │   └── models/
│   │       └── request_schemas.py
│   │
│   ├── services/                     # Core logic
│   │   ├── embedding_service.py
│   │   ├── search_service.py
│   │   └── metadata_service.py
│   │
│   ├── utils/                        # Helpers (optional)
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── data/                              # Your FAISS index + CSV
│   ├── faiss_index.bin
│   └── books_metadata_with_genre.csv
│
├── models/                            # Embedding model if local
│   └── sentence_transformer/
|
├── requirements.txt
└── README.md
