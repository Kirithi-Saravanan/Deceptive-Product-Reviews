import json
import os
from typing import Dict, Any

def save_data_quality_report(stats: Dict[str, Any], output_path: str):
    """Saves the data quality report to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=4)
