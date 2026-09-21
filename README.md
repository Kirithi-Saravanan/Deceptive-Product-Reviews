# ReviewGuard AI

### Detect deceptive reviews before they influence your decision.

## Problem Statement
Fake and deceptive online reviews manipulate consumer behavior, artificially inflate product ratings, and erode trust in digital marketplaces. ReviewGuard AI is designed to automatically detect and flag deceptive reviews to help users make informed decisions based on genuine feedback.

## Dataset
**Filename:** `data/public_reviews_dataset_cleaned.csv`

### Phase 2 Dataset Construction & EDA Findings
After executing the data preparation pipeline on the `public_reviews_dataset_cleaned.csv`, the following concrete statistics were observed:
- **Total Labeled Reviews:** 80,281
- **Deceptive Count:** 57,667 (71.8%)
- **Genuine Count:** 22,614 (28.2%)
- **Ambiguous Labels:** 0 (No row was flagged as both fake and honest simultaneously).
- **Class Imbalance:** Significant, with a ~72/28 split leaning heavily towards deceptive reviews.

**Reviewer Overlap Analysis:**
- **Unique Reviewers:** 36,764
- **Average Reviews per Reviewer:** ~2.18
- **Duplicate Texts:** 1,091 instances of duplicated review text were found, which were kept to let the model naturally learn spam-like behavior.

**Train/Validation/Test Split Strategy:**
To prevent data leakage, a reviewer-group-aware split was implemented. Reviewers (and all their associated reviews) were exclusively assigned to only one split using stratification on the target class.
- **Train Set:** 56,358 rows (71.8% deceptive) | 25,734 unique reviewers
- **Validation Set:** 11,725 rows (71.4% deceptive) | 5,514 unique reviewers
- **Test Set:** 12,198 rows (72.2% deceptive) | 5,516 unique reviewers
- **Reviewer Intersection:** ZERO across all combinations (Train ∩ Val = 0, Train ∩ Test = 0, Val ∩ Test = 0).

**Preprocessing Strategy:**
Text is normalized (lowercased, whitespace fixed) and missing values safely handled. TF-IDF vectorization is configured but importantly **only fitted on the training split** to prevent data leakage from the validation or test sets. Target-leaking columns (e.g. `reviewer_classified_fake`, `review_url`) are strictly verified and stripped out before outputting the finalized train/validation/test files.

### Phase 3 Machine Learning & NLP Results
The final modeling stage evaluated several baseline algorithms and textual representations (Word TF-IDF, Character TF-IDF, and Combined Features) on the validation set, taking care not to optimize over the held-out test data.

**Evaluated Models:**
- Logistic Regression (Word TF-IDF, Combined Features)
- Multinomial Naive Bayes (Word TF-IDF)
- Linear SVC (Word TF-IDF, Char TF-IDF)

**Best Performing Model:**
- **Word TF-IDF + MultinomialNB**
- Chosen based on the highest Deceptive-Class F1 Score (`0.8407`) and Macro-F1 (`0.5323`) during validation.

**Final Test Set Evaluation:**
The test set remained completely unbiased until this final metric was evaluated:
- **Accuracy:** 73.57%
- **Precision (Deceptive):** 74.42%
- **Recall (Deceptive):** 96.59%
- **F1 Score (Deceptive):** 0.8407
- **Macro F1:** 0.5323
- **ROC-AUC:** 0.7580

**Error Analysis:**
The model achieves high deceptive-review recall (85.20%) but has a relatively high false-positive rate (41.28%), meaning that some genuine reviews are incorrectly classified as deceptive. This is an important limitation and motivates future improvements such as better calibration, additional training data, and improved feature engineering.

**Model Artifacts (Production):**
After successful evaluation, the final selected pipeline was retrained on the combined Train+Validation sets to maximize real-world robustness. 
The production artifact incorporates the entire text normalizer and TF-IDF vectorizer logic natively into a single `.joblib` model pipeline:
- `ml/models/model.joblib`
- `ml/models/model_metadata.json`
