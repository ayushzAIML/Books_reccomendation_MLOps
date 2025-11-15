name: CI-CD

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest -q

  run_pipeline:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: python-version: '3.10'
      - name: Install deps
        run: pip install -r requirements.txt zenml mlflow faiss-cpu
      - name: Run ZenML pipeline
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python src/pipelines/zenml_pipeline.py
      - name: Build Docker (optional deploy)
        run: |
          docker build -t ${{ secrets.DOCKER_REGISTRY }}/books-recommender:${{ github.sha }} .
          echo "docker push skipped in example"
