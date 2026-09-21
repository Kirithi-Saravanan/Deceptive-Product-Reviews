import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data_loader import load_dataset
from label_builder import construct_labels, remove_leakage_columns
from text_features import build_text_features
from eda import generate_eda_plots
from split_data import grouped_train_val_test_split
from data_quality import save_data_quality_report
from preprocessing import normalize_text, fit_tfidf

def main():
    print("Loading dataset...")
    df = load_dataset('data/public_reviews_dataset_cleaned.csv')
    
    print("Constructing labels...")
    labeled_df, stats = construct_labels(df)
    
    # Reviewer Overlap Analysis globally
    stats['unique_reviewers_total'] = labeled_df['reviewer_id'].nunique()
    stats['reviews_per_reviewer_avg'] = len(labeled_df) / stats['unique_reviewers_total'] if stats['unique_reviewers_total'] > 0 else 0
    
    print("Engineering features...")
    labeled_df = build_text_features(labeled_df)
    labeled_df['normalized_text'] = labeled_df['review_text'].apply(normalize_text)
    
    print("Generating EDA...")
    generate_eda_plots(labeled_df, 'ml/results/eda')
    
    print("Splitting data...")
    train_df, val_df, test_df, split_stats = grouped_train_val_test_split(labeled_df, 'reviewer_id', 'target')
    stats.update(split_stats)
    
    # Check duplicate texts
    stats['duplicate_texts'] = int(labeled_df['review_text'].duplicated().sum())
    
    print("Removing leakage columns & saving splits...")
    # Remove leakage for all splits before saving
    train_df = remove_leakage_columns(train_df, retain_for_grouping=True)
    val_df = remove_leakage_columns(val_df, retain_for_grouping=True)
    test_df = remove_leakage_columns(test_df, retain_for_grouping=True)
    
    # Assertions to ensure leakage cols are gone
    leakage_cols = ['reviewer_classified_fake', 'reviewer_labeled_fake', 'fake_review_product']
    for col in leakage_cols:
        assert col not in train_df.columns, f"Leakage column {col} found in train!"
        assert col not in val_df.columns, f"Leakage column {col} found in val!"
        assert col not in test_df.columns, f"Leakage column {col} found in test!"
        
    os.makedirs('ml/data', exist_ok=True)
    
    # Save the splits
    train_df.to_csv('ml/data/train.csv', index=False)
    val_df.to_csv('ml/data/validation.csv', index=False)
    test_df.to_csv('ml/data/test.csv', index=False)
    
    # Also save the overall labeled dataset for completeness
    labeled_df_clean = remove_leakage_columns(labeled_df, retain_for_grouping=True)
    labeled_df_clean.to_csv('ml/data/labeled_reviews.csv', index=False)
    
    # Fitting TF-IDF *ONLY* on train text (just validating the function runs)
    print("Fitting TF-IDF on train text only...")
    _ = fit_tfidf(train_df['normalized_text'])
    
    print("Saving quality report...")
    save_data_quality_report(stats, 'ml/results/data_quality_report.json')
    
    print("Pipeline Complete. Data Quality Stats:")
    for k, v in stats.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
