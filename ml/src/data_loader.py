import pandas as pd
import numpy as np

def load_dataset(file_path: str) -> pd.DataFrame:
    """Loads the dataset safely."""
    df = pd.read_csv(file_path, low_memory=False)
    # Convert appropriate text columns to string and handle nulls
    if 'review_text' in df.columns:
        df['review_text'] = df['review_text'].astype(str).replace('nan', '')
    if 'review_title' in df.columns:
        df['review_title'] = df['review_title'].astype(str).replace('nan', '')
    return df
