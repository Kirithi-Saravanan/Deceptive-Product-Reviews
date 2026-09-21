import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple

def normalize_text(text: str) -> str:
    """Basic text normalization (lowercase, whitespace)"""
    if not isinstance(text, str):
        text = str(text) if pd.notnull(text) else ""
    text = text.lower()
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fit_tfidf(train_texts: pd.Series, max_features: int = 5000, min_df: int = 5) -> TfidfVectorizer:
    """Fits TF-IDF only on training text."""
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=min_df,
        sublinear_tf=True,
        stop_words=None # Configurable later
    )
    vectorizer.fit(train_texts)
    return vectorizer

def transform_tfidf(vectorizer: TfidfVectorizer, texts: pd.Series):
    """Transforms validation/test sets using fitted vectorizer."""
    return vectorizer.transform(texts)
