#!/usr/bin/env python
# quick_start.py - Quick start script to run the app

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command"""
    if description:
        print(f"🔨 {description}")
    print(f"   → {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error: Command failed")
        return False
    return True

def main():
    print("🧩 SAP Intelligent Assistant - Quick Start")
    print("=" * 50)
    print()
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Run: python setup.sh")
        sys.exit(1)
    
    # Activate venv and check if RAG index exists
    index_path = Path("data/rag_index.faiss")
    
    if not index_path.exists():
        print("⚠️  RAG index not found. Building dataset and index...")
        print()
        
        # Build dataset
        if not run_command(
            "source .venv/bin/activate && python tools/build_dataset.py",
            "Building dataset from web sources"
        ):
            sys.exit(1)
        
        print()
        
        # Build index
        if not run_command(
            "source .venv/bin/activate && python tools/embeddings.py",
            "Building RAG index"
        ):
            sys.exit(1)
    
    print()
    print("✅ All systems ready!")
    print()
    print("Starting Streamlit app...")
    print()
    
    # Run streamlit
    os.system("source .venv/bin/activate && streamlit run app.py")

if __name__ == "__main__":
    main()
