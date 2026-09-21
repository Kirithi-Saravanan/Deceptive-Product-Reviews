import pandas as pd
import re

def build_text_features(df: pd.DataFrame, text_col: str = 'review_text') -> pd.DataFrame:
    """Engineers basic text features from the review text."""
    # Ensure text is string and handle nulls
    texts = df[text_col].fillna("").astype(str)
    
    # Feature calculation
    df['char_count'] = texts.apply(len)
    df['word_count'] = texts.apply(lambda x: len(x.split()))
    df['sentence_count'] = texts.apply(lambda x: len(re.split(r'[.!?]+', x)) - 1)
    df['sentence_count'] = df['sentence_count'].apply(lambda x: 1 if x == 0 else x)
    df['avg_word_length'] = df['char_count'] / (df['word_count'] + 1)
    
    df['exclamation_count'] = texts.apply(lambda x: x.count('!'))
    df['question_count'] = texts.apply(lambda x: x.count('?'))
    df['repeated_punct_count'] = texts.apply(lambda x: len(re.findall(r'([.!?])\1+', x)))
    
    df['uppercase_ratio'] = texts.apply(lambda x: sum(1 for c in x if c.isupper()) / (len(x) + 1))
    df['digit_count'] = texts.apply(lambda x: sum(1 for c in x if c.isdigit()))
    df['url_count'] = texts.apply(lambda x: len(re.findall(r'http[s]?://\S+', x)))
    
    df['unique_word_ratio'] = texts.apply(lambda x: len(set(x.split())) / (len(x.split()) + 1))
    
    return df
