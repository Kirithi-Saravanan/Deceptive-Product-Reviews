from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB, ComplementNB

from feature_transformers import TextNormalizer, EngineeredFeaturesExtractor


def build_text_pipeline(classifier, vectorizer_type='word', ngram_range=(1, 2), max_features=5000, min_df=5):
    """Builds a pipeline using only text features."""

    if vectorizer_type == 'word':
        vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            sublinear_tf=True
        )
    elif vectorizer_type == 'char':
        vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=ngram_range,
            max_features=max_features,
            min_df=min_df,
            sublinear_tf=True
        )
    else:
        raise ValueError("vectorizer_type must be 'word' or 'char'")

    pipeline = Pipeline([
        ('text_norm', TextNormalizer()),
        ('tfidf', vectorizer),
        ('clf', classifier)
    ])
    return pipeline


def build_combined_pipeline(classifier, word_max_features=5000, char_max_features=5000):
    """Builds a pipeline combining word TF-IDF and engineered features."""

    word_tfidf = Pipeline([
        ('text_norm', TextNormalizer()),
        ('tfidf', TfidfVectorizer(
            analyzer='word', ngram_range=(1, 2),
            max_features=word_max_features, min_df=5, sublinear_tf=True
        ))
    ])

    # word_tfidf is applied to the 'review_text' column;
    # engineered features are applied to the full DataFrame.
    preprocessor = ColumnTransformer(
        transformers=[
            ('word_tfidf', word_tfidf, 'review_text'),
            ('engineered', Pipeline([
                ('extractor', EngineeredFeaturesExtractor()),
                ('scaler', StandardScaler(with_mean=False))
            ]), ['review_text', 'review_rating', 'number_of_helpful', 'number_of_photos'])
        ],
        remainder='drop'
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('clf', classifier)
    ])
    return pipeline


def get_classifier(model_name: str, **kwargs):
    """
    Returns a scikit-learn classifier instance.

    Parameters
    ----------
    model_name : str
        One of: "LogisticRegression", "LinearSVC", "MultinomialNB", "ComplementNB".
    **kwargs
        Extra keyword arguments forwarded to the classifier constructor.
        Relevant for MultinomialNB:
            fit_prior   (bool)       – learn class priors from data (default True).
            class_prior (list|None)  – fixed class priors, e.g. [0.3, 0.7].
    """
    if model_name == "LogisticRegression":
        return LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    elif model_name == "LinearSVC":
        return LinearSVC(class_weight='balanced', dual=False, max_iter=2000, random_state=42)
    elif model_name == "MultinomialNB":
        return MultinomialNB(
            fit_prior=kwargs.get('fit_prior', True),
            class_prior=kwargs.get('class_prior', None)
        )
    elif model_name == "ComplementNB":
        return ComplementNB()
    else:
        raise ValueError(f"Unknown classifier: {model_name}")
