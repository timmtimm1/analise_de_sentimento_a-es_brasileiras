"""FinBERT sentiment scoring, extracted from main.ipynb so both the
notebook and company_pipeline.py can reuse it without duplicating logic.

The model is loaded lazily on first use so importing this module (e.g. to
inspect functions, or from code paths that never call it) doesn't force a
FinBERT download/load.
"""

import pandas as pd
from tqdm import tqdm

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _model is None:
        import torch  # noqa: F401  (imported for side effect of registering backend)
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        model_name = "ProsusAI/finbert"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return _tokenizer, _model


def get_sentiment_scores(text: str) -> tuple[float, float, float]:
    import torch

    tokenizer, model = _load_model()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # FinBERT returns scores in the order [positive, negative, neutral]
    positive_score = probabilities[0, 0].item()
    negative_score = probabilities[0, 1].item()
    neutral_score = probabilities[0, 2].item()

    return positive_score, negative_score, neutral_score


def analyze_sentiment_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    positive_scores = []
    negative_scores = []
    neutral_scores = []
    overall_sentiments = []

    for title in tqdm(df["title"], desc="Analyzing sentiment"):
        pos, neg, neu = get_sentiment_scores(title)
        positive_scores.append(pos)
        negative_scores.append(neg)
        neutral_scores.append(neu)

        max_score = max(pos, neg, neu)
        if max_score == pos:
            overall_sentiments.append("Positive")
        elif max_score == neg:
            overall_sentiments.append("Negative")
        else:
            overall_sentiments.append("Neutral")

    df["positive_score"] = positive_scores
    df["negative_score"] = negative_scores
    df["neutral_score"] = neutral_scores
    df["overall_sentiment"] = overall_sentiments

    return df


def analyze_sentiment(csv_file) -> pd.DataFrame:
    return analyze_sentiment_df(pd.read_csv(csv_file))
