import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import re

class TextNormalizer(BaseEstimator, TransformerMixin):
    """Custom transformer to normalize text inside the pipeline."""
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        # X is expected to be a pandas Series or list of strings
        if isinstance(X, pd.DataFrame):
            X = X.iloc[:, 0]
        
        normalized = []
        for text in X:
            if pd.isnull(text):
                t = ""
            else:
                t = str(text)
            t = t.lower()
            t = re.sub(r'\s+', ' ', t).strip()
            normalized.append(t)
        return pd.Series(normalized)

class EngineeredFeaturesExtractor(BaseEstimator, TransformerMixin):
    """Custom transformer to extract numeric features from the raw DataFrame."""
    def fit(self, X, y=None):
        return self
        
    def transform(self, X, y=None):
        # X is expected to be a DataFrame containing 'review_text' and other metadata
        df_feats = pd.DataFrame(index=X.index)
        
        texts = X['review_text'].fillna("").astype(str)
        
        # Text features
        df_feats['char_count'] = texts.apply(len)
        df_feats['word_count'] = texts.apply(lambda x: len(x.split()))
        df_feats['sentence_count'] = texts.apply(lambda x: len(re.split(r'[.!?]+', x)) - 1)
        df_feats['sentence_count'] = df_feats['sentence_count'].apply(lambda x: 1 if x == 0 else x)
        df_feats['avg_word_length'] = df_feats['char_count'] / (df_feats['word_count'] + 1)
        
        df_feats['exclamation_count'] = texts.apply(lambda x: x.count('!'))
        df_feats['question_count'] = texts.apply(lambda x: x.count('?'))
        df_feats['repeated_punct_count'] = texts.apply(lambda x: len(re.findall(r'([.!?])\1+', x)))
        
        df_feats['uppercase_ratio'] = texts.apply(lambda x: sum(1 for c in x if c.isupper()) / (len(x) + 1))
        df_feats['digit_count'] = texts.apply(lambda x: sum(1 for c in x if c.isdigit()))
        df_feats['url_count'] = texts.apply(lambda x: len(re.findall(r'http[s]?://\S+', x)))
        df_feats['unique_word_ratio'] = texts.apply(lambda x: len(set(x.split())) / (len(x.split()) + 1))
        
        # Metadata features (if present, else 0)
        df_feats['review_rating'] = X.get('review_rating', pd.Series(np.zeros(len(X)), index=X.index)).fillna(0)
        df_feats['number_of_helpful'] = X.get('number_of_helpful', pd.Series(np.zeros(len(X)), index=X.index)).fillna(0)
        df_feats['number_of_photos'] = X.get('number_of_photos', pd.Series(np.zeros(len(X)), index=X.index)).fillna(0)
        
        return df_feats.values
