from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

@router.get("/info")
def get_model_info():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    metadata_path = project_root / 'ml' / 'models' / 'model_metadata.json'
    
    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    # Flatten useful fields for easy consumption
    val_metrics = metadata.get('validation_metrics', {})
    test_metrics = metadata.get('final_test_metrics', {})
    
    return {
        "selected_model": metadata.get("selected_model"),
        "selected_threshold": metadata.get("selected_threshold"),
        "features": metadata.get("features"),
        "train_size": metadata.get("train_size"),
        "val_size": metadata.get("val_size"),
        "test_size": metadata.get("test_size"),
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
    }
