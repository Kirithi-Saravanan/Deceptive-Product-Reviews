import pandas as pd
import numpy as np

file_path = 'data/public_reviews_dataset_cleaned.csv'
print(f"Loading {file_path}...")
df = pd.read_csv(file_path, low_memory=False)

print("\n--- Shape ---")
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

print("\n--- Column Names & Data Types ---")
print(df.dtypes)

print("\n--- Missing Value Counts ---")
print(df.isnull().sum())

print("\n--- Duplicate Row Count ---")
print(f"Duplicate rows: {df.duplicated().sum()}")

print("\n--- Unique Value Counts for Categorical/Boolean ---")
categorical_cols = df.select_dtypes(include=['object', 'bool']).columns
for col in categorical_cols:
    if df[col].nunique() < 20:
        print(f"\nValue counts for {col}:")
        print(df[col].value_counts(dropna=False))

print("\n--- Review-Rating Distribution ---")
if 'rating' in df.columns:
    print(df['rating'].value_counts(dropna=False))
elif 'review_rating' in df.columns:
    print(df['review_rating'].value_counts(dropna=False))
else:
    for col in df.columns:
        if 'rating' in col.lower() or 'stars' in col.lower():
            print(f"Possible rating column '{col}':")
            print(df[col].value_counts(dropna=False))

print("\n--- Review-Text Length Statistics ---")
text_col = None
if 'review_text' in df.columns:
    text_col = 'review_text'
elif 'text' in df.columns:
    text_col = 'text'
elif 'review' in df.columns:
    text_col = 'review'

if text_col:
    df['text_len'] = df[text_col].astype(str).apply(len)
    print(df['text_len'].describe())
else:
    print("Could not identify review text column.")

print("\n--- Date Range ---")
date_col = None
if 'date' in df.columns:
    date_col = 'date'
elif 'review_date' in df.columns:
    date_col = 'review_date'
elif 'timestamp' in df.columns:
    date_col = 'timestamp'

if date_col:
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        print(f"Min date: {df[date_col].min()}")
        print(f"Max date: {df[date_col].max()}")
    except:
        print(f"Column '{date_col}' exists but could not be parsed as datetime.")
else:
    print("Could not identify date column.")

print("\n--- Label-Related Columns ---")
label_candidates = ['reviewer_classified_fake', 'reviewer_classified_honest', 
                    'reviewer_labeled_fake', 'reviewer_labeled_honest', 
                    'fake_review_product', 'review_is_removed_by_amazon',
                    'label', 'is_fake', 'is_deceptive', 'fraud']
for col in df.columns:
    if col in label_candidates or 'fake' in col.lower() or 'honest' in col.lower() or 'decept' in col.lower():
        print(f"\nDistribution of '{col}':")
        print(df[col].value_counts(dropna=False))
