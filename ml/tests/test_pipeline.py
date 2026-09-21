import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from label_builder import construct_labels, remove_leakage_columns
from text_features import build_text_features
from preprocessing import normalize_text, fit_tfidf
from split_data import grouped_train_val_test_split

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'reviewer_id': ['r1', 'r1', 'r2', 'r3', 'r4', 'r5'],
        'reviewer_classified_fake': [True, True, False, False, True, False],
        'reviewer_classified_honest': [False, False, True, True, True, False],
        'review_text': ['Bad!', 'Very bad', 'Good.', 'Okay.', 'Ambiguous', 'No label'],
        'fake_review_product': [True, False, False, False, False, False],
        'review_is_removed_by_amazon': [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    })

def test_construct_labels(sample_df):
    labeled, stats = construct_labels(sample_df)
    
    assert stats['ambiguous_count'] == 1 # r4 is ambiguous
    assert stats['total_labeled_count'] == 4 # r1, r1, r2, r3
    
    assert len(labeled) == 4
    # r5 has neither fake nor honest -> excluded
    assert 'No label' not in labeled['review_text'].values
    
def test_leakage_removal(sample_df):
    clean_df = remove_leakage_columns(sample_df, retain_for_grouping=True)
    assert 'reviewer_classified_fake' not in clean_df.columns
    assert 'fake_review_product' not in clean_df.columns
    assert 'reviewer_id' in clean_df.columns # Retained for grouping

def test_split_no_overlap():
    df = pd.DataFrame({
        'reviewer_id': [f'r{i}' for i in range(100)] * 2, # 100 reviewers, 2 reviews each
        'target': np.random.randint(0, 2, 200)
    })
    
    train, val, test, stats = grouped_train_val_test_split(df, 'reviewer_id', 'target')
    assert stats['overlap_train_val'] == 0
    assert stats['overlap_train_test'] == 0
    assert stats['overlap_val_test'] == 0
    
def test_preprocessing():
    assert normalize_text(" Hello   World! ") == "hello world!"
    assert normalize_text(np.nan) == ""

def test_tfidf_fit():
    train_texts = pd.Series(["hello world", "fake review", "this is genuine"])
    vectorizer = fit_tfidf(train_texts, max_features=10, min_df=1)
    
    val_texts = pd.Series(["hello there"])
    transformed = vectorizer.transform(val_texts)
    
    assert transformed.shape[1] <= 10 # Features limited
    assert transformed.shape[0] == 1
