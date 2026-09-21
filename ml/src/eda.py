import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def generate_eda_plots(df: pd.DataFrame, output_dir: str):
    """Generates EDA visualizations."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Class distribution
    if 'target' in df.columns:
        plt.figure(figsize=(6, 4))
        sns.countplot(data=df, x='target', palette='Set2')
        plt.title('Target Class Distribution (0=Genuine, 1=Deceptive)')
        plt.savefig(f"{output_dir}/class_distribution.png")
        plt.close()
        
        # Rating by Target Class
        if 'review_rating' in df.columns:
            plt.figure(figsize=(8, 5))
            sns.countplot(data=df, x='review_rating', hue='target', palette='Set2')
            plt.title('Review Rating by Target Class')
            plt.savefig(f"{output_dir}/rating_by_class.png")
            plt.close()

    # 2. Rating distribution overall
    if 'review_rating' in df.columns:
        plt.figure(figsize=(6, 4))
        sns.countplot(data=df, x='review_rating', palette='viridis')
        plt.title('Overall Review Rating Distribution')
        plt.savefig(f"{output_dir}/rating_distribution.png")
        plt.close()

    # 3. Review length distribution
    if 'char_count' in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[df['char_count'] < 5000]['char_count'], bins=50, kde=True)
        plt.title('Review Length Distribution (Char Count < 5000)')
        plt.savefig(f"{output_dir}/review_length_dist.png")
        plt.close()
        
    # 4. Review count per reviewer
    if 'reviewer_id' in df.columns:
        counts = df['reviewer_id'].value_counts()
        plt.figure(figsize=(8, 5))
        sns.histplot(counts[counts < 20], bins=20)
        plt.title('Reviews per Reviewer (for count < 20)')
        plt.savefig(f"{output_dir}/reviewer_counts.png")
        plt.close()
