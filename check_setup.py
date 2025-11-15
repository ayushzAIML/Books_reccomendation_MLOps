#!/usr/bin/env python3
"""
Quick test script to verify ZenML pipeline setup
Run this to diagnose any issues with artifact/model loading
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_artifacts():
    """Check if all required artifact files exist."""
    print("\n" + "="*80)
    print("🔍 Checking Artifacts...")
    print("="*80)
    
    from src.config import (
        META_CSV, EMB_NPY, FAISS_INDEX, ISBN_LIST, 
        RATINGS_CSV, USER_PROFILE_PATH
    )
    
    artifacts = {
        "📖 Metadata CSV": META_CSV,
        "📊 Embeddings NPY": EMB_NPY,
        "🔗 FAISS Index": FAISS_INDEX,
        "🏷️ ISBN List": ISBN_LIST,
        "⭐ Ratings CSV (optional)": RATINGS_CSV,
        "👤 User Profiles": USER_PROFILE_PATH,
    }
    
    found = 0
    missing = 0
    
    for name, path in artifacts.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"✓ {name}")
            print(f"  └─ {path} ({size_mb:.2f} MB)")
            found += 1
        else:
            print(f"✗ {name}")
            print(f"  └─ {path} (NOT FOUND)")
            missing += 1
    
    print(f"\nResult: {found} found, {missing} missing")
    return missing == 0


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "="*80)
    print("📦 Checking Dependencies...")
    print("="*80)
    
    required = {
        "zenml": "ZenML orchestration",
        "pandas": "Data manipulation",
        "numpy": "Numerical operations",
        "faiss": "Vector search",
        "sentence_transformers": "Bi-encoder & Cross-encoder models",
        "sklearn": "Preprocessing",
        "fastapi": "API framework",
    }
    
    found = 0
    missing = 0
    
    for pkg, description in required.items():
        try:
            __import__(pkg if pkg != "sklearn" else "sklearn")
            print(f"✓ {pkg:25} - {description}")
            found += 1
        except ImportError:
            print(f"✗ {pkg:25} - {description}")
            missing += 1
    
    print(f"\nResult: {found} found, {missing} missing")
    if missing > 0:
        print("\n⚠️  Install missing packages:")
        print("   pip install -r requirements.txt")
    
    return missing == 0


def check_configuration():
    """Check if configuration is properly set."""
    print("\n" + "="*80)
    print("⚙️  Checking Configuration...")
    print("="*80)
    
    from src.config import (
        BI_ENCODER_MODEL, CROSS_ENCODER_MODEL,
        W_CE, W_GENRE, W_USER, W_SESSION,
        RETRIEVE_TOP, FINAL_K
    )
    
    print(f"✓ Bi-encoder:       {BI_ENCODER_MODEL}")
    print(f"✓ Cross-encoder:    {CROSS_ENCODER_MODEL}")
    print(f"✓ Recommendation weights:")
    print(f"  - CE (semantic):  {W_CE}")
    print(f"  - Genre:          {W_GENRE}")
    print(f"  - User:           {W_USER}")
    print(f"  - Session:        {W_SESSION}")
    print(f"  - Total:          {W_CE + W_GENRE + W_USER + W_SESSION}")
    print(f"✓ Retrieve top:     {RETRIEVE_TOP}")
    print(f"✓ Final K:          {FINAL_K}")
    
    # Validate weights sum to 1.0
    weight_sum = W_CE + W_GENRE + W_USER + W_SESSION
    if abs(weight_sum - 1.0) < 0.001:
        print("\n✓ Configuration valid!")
        return True
    else:
        print(f"\n✗ Weights don't sum to 1.0: {weight_sum}")
        return False


def test_pipeline():
    """Test running the pipeline."""
    print("\n" + "="*80)
    print("🚀 Testing Pipeline Execution...")
    print("="*80)
    
    try:
        from src.zenml_pipelines import books_recommendation_initialization
        
        print("Executing pipeline...")
        result = books_recommendation_initialization()
        
        print("\n✅ Pipeline execution successful!")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"\n✗ Pipeline execution failed:")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("\n" + "="*80)
    print("🔧 Books Recommendation System - Health Check")
    print("="*80)
    
    results = {
        "Artifacts": check_artifacts(),
        "Dependencies": check_dependencies(),
        "Configuration": check_configuration(),
        "Pipeline": test_pipeline(),
    }
    
    print("\n" + "="*80)
    print("📊 Summary")
    print("="*80)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check:20} {status}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*80)
    if all_pass:
        print("✅ All checks passed! System is ready.")
    else:
        print("❌ Some checks failed. Please review the output above.")
    print("="*80 + "\n")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
