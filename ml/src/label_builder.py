import pandas as pd
from typing import Tuple, Dict, Any

def construct_labels(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Constructs the binary target label based on criteria:
    reviewer_classified_fake == True -> 1
    reviewer_classified_honest == True -> 0
    Returns the labeled subset and a stats dictionary.
    """
    # Check for ambiguous labels
    ambiguous_mask = (df['reviewer_classified_fake'] == True) & (df['reviewer_classified_honest'] == True)
    ambiguous_count = ambiguous_mask.sum()
    
    # Filter out ambiguous
    df_clean = df[~ambiguous_mask].copy()
    
    fake_mask = df_clean['reviewer_classified_fake'] == True
    honest_mask = df_clean['reviewer_classified_honest'] == True
    
    # Rows with neither condition are ignored for supervised learning
    labeled_mask = fake_mask | honest_mask
    labeled_df = df_clean[labeled_mask].copy()
    
    # Create target column
    labeled_df['target'] = 0
    labeled_df.loc[labeled_df['reviewer_classified_fake'] == True, 'target'] = 1
    
    deceptive_count = (labeled_df['target'] == 1).sum()
    genuine_count = (labeled_df['target'] == 0).sum()
    total_labeled = len(labeled_df)
    
    stats = {
        'ambiguous_count': int(ambiguous_count),
        'total_labeled_count': int(total_labeled),
        'deceptive_count': int(deceptive_count),
        'genuine_count': int(genuine_count),
        'deceptive_pct': float(deceptive_count / total_labeled * 100) if total_labeled > 0 else 0.0,
        'genuine_pct': float(genuine_count / total_labeled * 100) if total_labeled > 0 else 0.0
    }
    
    return labeled_df, stats

def remove_leakage_columns(df: pd.DataFrame, retain_for_grouping: bool = True) -> pd.DataFrame:
    """Removes columns that leak target information or could cause overfitting."""
    leakage_cols = [
        'reviewer_classified_fake',
        'reviewer_classified_honest',
        'reviewer_labeled_fake',
        'reviewer_labeled_honest',
        'fake_review_product',
        'review_is_removed_by_amazon',
        'fake_review_campaign_start_date',
        'review_url',
        'reviewer_url'
    ]
    
    if not retain_for_grouping:
        leakage_cols.append('reviewer_id')
        
    cols_to_drop = [c for c in leakage_cols if c in df.columns]
    return df.drop(columns=cols_to_drop)
