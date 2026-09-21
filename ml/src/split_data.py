import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from typing import Tuple, Dict

def grouped_train_val_test_split(df: pd.DataFrame, group_col: str, target_col: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict]:
    """
    Performs a reviewer-group-aware split ensuring zero reviewer overlap.
    Uses StratifiedGroupKFold to approximate 70/15/15 split.
    """
    # We want approx 70% train, 15% val, 15% test.
    # We can do this by splitting 70/30 first, then splitting the 30 into 50/50.
    
    # First split: 70/30
    cv1 = StratifiedGroupKFold(n_splits=3) # Actually, KFold with 3 is 66/33. Let's use 4 splits (75/25), or just random groups.
    # To get ~70/15/15 exactly with StratifiedGroupKFold is tricky since n_splits is integer.
    # Let's use n_splits=5 (80/20) or n_splits=7 (85/15).
    # Since we need 70/15/15, we can use an approach: assign groups to folds randomly but preserving stratification.
    # Let's use a custom approach to guarantee no overlap.
    
    unique_groups = df[group_col].unique()
    
    # Actually, StratifiedGroupKFold gives us generator. Let's use n_splits=10.
    cv = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=42)
    folds = list(cv.split(df, df[target_col], df[group_col]))
    
    # fold 0, 1, 2, 3, 4, 5, 6 -> Train (70%)
    # fold 7, 8 -> Val (~20%, let's say fold 7 is 10%, actually 10 splits means each fold is 10%)
    # So: Train (folds 0-6 = 70%), Val (fold 7, 8 = 20% -> actually let's do folds 7 and half of 8? No, keep folds intact).
    # Train: 0,1,2,3,4,5,6 (70%)
    # Val: 7 (10%?) Wait, 10 splits = 10% each. Let's do 70% train, 10% val, 20% test or similar. 
    # Let's use n_splits=7 for 14.2% each? 
    # Or just use the standard scikit-learn approach:
    # We can use np.random.choice on the unique groups to achieve the exact ratio.
    
    # Better yet, since we don't have a strict ratio requirement (approx 70/15/15):
    # Let's assign each group to train, val, test with probability 0.7, 0.15, 0.15.
    
    np.random.seed(42)
    # Stratified split is requested, so we should try to keep the class distribution.
    # A simple way: find the primary class for each group, then stratify on that.
    group_majority_class = df.groupby(group_col)[target_col].agg(lambda x: pd.Series.mode(x)[0]).reset_index()
    
    train_groups = []
    val_groups = []
    test_groups = []
    
    # Stratify by majority class of the group
    for cls in [0, 1]:
        cls_groups = group_majority_class[group_majority_class[target_col] == cls][group_col].values
        np.random.shuffle(cls_groups)
        
        n_train = int(len(cls_groups) * 0.70)
        n_val = int(len(cls_groups) * 0.15)
        
        train_groups.extend(cls_groups[:n_train])
        val_groups.extend(cls_groups[n_train:n_train+n_val])
        test_groups.extend(cls_groups[n_train+n_val:])
        
    train_df = df[df[group_col].isin(train_groups)].copy()
    val_df = df[df[group_col].isin(val_groups)].copy()
    test_df = df[df[group_col].isin(test_groups)].copy()
    
    stats = {
        'train_size': len(train_df),
        'val_size': len(val_df),
        'test_size': len(test_df),
        'train_deceptive_pct': (train_df[target_col] == 1).mean() * 100 if len(train_df) > 0 else 0,
        'val_deceptive_pct': (val_df[target_col] == 1).mean() * 100 if len(val_df) > 0 else 0,
        'test_deceptive_pct': (test_df[target_col] == 1).mean() * 100 if len(test_df) > 0 else 0,
        'train_unique_reviewers': train_df[group_col].nunique(),
        'val_unique_reviewers': val_df[group_col].nunique(),
        'test_unique_reviewers': test_df[group_col].nunique(),
        'overlap_train_val': len(set(train_groups).intersection(set(val_groups))),
        'overlap_train_test': len(set(train_groups).intersection(set(test_groups))),
        'overlap_val_test': len(set(val_groups).intersection(set(test_groups)))
    }
    
    return train_df, val_df, test_df, stats
