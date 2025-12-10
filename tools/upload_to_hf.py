
# tools/upload_to_hf.py
import os
from huggingface_hub import HfApi, create_repo
import json
from pathlib import Path

def upload_dataset():
    """Upload dataset to Hugging Face using GitHub secrets"""
    
    # Get credentials from GitHub secrets
    hf_token = os.getenv("HF_TOKEN")
    hf_repo = os.getenv("HF_DATASET_REPO")
    
    if not hf_token:
        raise ValueError("❌ HF_TOKEN secret not found in GitHub")
    if not hf_repo:
        raise ValueError("❌ HF_DATASET_REPO secret not found in GitHub")
    
    print(f"📤 Uploading to Hugging Face: {hf_repo}")
    
    # Initialize HF API
    api = HfApi(token=hf_token)
    
    # Create repo if it doesn't exist
    try:
        create_repo(repo_id=hf_repo, repo_type="dataset", exist_ok=True, token=hf_token)
        print("✅ Repository ready")
    except Exception as e:
        print(f"⚠️  Note: {e}")
    
    # Upload dataset file
    dataset_path = "data/sap_dataset.json"
    if Path(dataset_path).exists():
        api.upload_file(
            path_or_fileobj=dataset_path,
            path_in_repo="sap_dataset.json",
            repo_id=hf_repo,
            repo_type="dataset",
            token=hf_token
        )
        print(f"✅ Dataset uploaded successfully to {hf_repo}")
        
        # Also upload a dataset card
        dataset_card = {
            "dataset_name": "SAP Knowledge Base",
            "description": "Multi-source SAP dataset (Community, StackOverflow, GitHub, Dev.to, Medium, SAP Developers tutorials)",
            "language": "en",
            "task_categories": ["question-answering", "text-generation"],
            "tags": ["sap", "basis", "abap", "hana", "btp", "fiori", "ui5", "qa"]
        }
        
        with open("data/dataset_card.json", "w") as f:
            json.dump(dataset_card, f, indent=2)
            
        api.upload_file(
            path_or_fileobj="data/dataset_card.json",
            path_in_repo="dataset_card.json",
            repo_id=hf_repo,
            repo_type="dataset",
            token=hf_token
        )
        print("✅ Dataset card uploaded")
        
    else:
        print(f"❌ Dataset file {dataset_path} not found")

if __name__ == "__main__":
    upload_dataset()
