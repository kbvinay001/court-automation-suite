"""
Case Predictor - ML model for predicting hearing likelihood and case outcomes.
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "trained_models")
os.makedirs(MODEL_DIR, exist_ok=True)


class CasePredictor:
    """ML model to predict hearing likelihood and case outcomes."""

    def __init__(self):
        self.hearing_model: Optional[RandomForestClassifier] = None
        self.outcome_model: Optional[GradientBoostingClassifier] = None
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler = StandardScaler()
        self.feature_columns: List[str] = []
        self._load_models()

    def _load_models(self):
        """Load pre-trained models if available."""
        hearing_path = os.path.join(MODEL_DIR, "hearing_predictor.pkl")
        outcome_path = os.path.join(MODEL_DIR, "outcome_predictor.pkl")
        encoders_path = os.path.join(MODEL_DIR, "label_encoders.pkl")
        scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")

        try:
            if os.path.exists(hearing_path):
                with open(hearing_path, "rb") as f:
                    self.hearing_model = pickle.load(f)
                logger.info("Loaded hearing prediction model")

            if os.path.exists(outcome_path):
                with open(outcome_path, "rb") as f:
                    self.outcome_model = pickle.load(f)
                logger.info("Loaded outcome prediction model")

            if os.path.exists(encoders_path):
                with open(encoders_path, "rb") as f:
                    self.label_encoders = pickle.load(f)

            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
        except Exception as e:
            logger.warning(f"Could not load models: {e}")

    def _save_models(self):
        """Save trained models to disk."""
        try:
            with open(os.path.join(MODEL_DIR, "hearing_predictor.pkl"), "wb") as f:
                pickle.dump(self.hearing_model, f)
            with open(os.path.join(MODEL_DIR, "outcome_predictor.pkl"), "wb") as f:
                pickle.dump(self.outcome_model, f)
            with open(os.path.join(MODEL_DIR, "label_encoders.pkl"), "wb") as f:
                pickle.dump(self.label_encoders, f)
            with open(os.path.join(MODEL_DIR, "scaler.pkl"), "wb") as f:
                pickle.dump(self.scaler, f)
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Model save failed: {e}")

    def prepare_features(self, cases: List[Dict]) -> pd.DataFrame:
        """Convert case data to feature DataFrame."""
        records = []
        for case in cases:
            hearings = case.get("hearings", [])
            filing_date = case.get("filing_date")
            next_date = case.get("next_hearing_date")

            # Calculate derived features
            days_pending = 0
            if filing_date:
                try:
                    filed = datetime.fromisoformat(str(filing_date)).date()
                    days_pending = (date.today() - filed).days
                except (ValueError, TypeError):
                    pass

            days_to_hearing = 0
            if next_date:
                try:
                    hearing = datetime.fromisoformat(str(next_date)).date()
                    days_to_hearing = (hearing - date.today()).days
                except (ValueError, TypeError):
                    pass

            # Average days between hearings
            avg_gap = 0
            if len(hearings) >= 2:
                gaps = []
                for i in range(1, len(hearings)):
                    try:
                        d1 = datetime.fromisoformat(str(hearings[i - 1].get("date", ""))).date()
                        d2 = datetime.fromisoformat(str(hearings[i].get("date", ""))).date()
                        gaps.append((d2 - d1).days)
                    except (ValueError, TypeError):
                        pass
                avg_gap = np.mean(gaps) if gaps else 0

            record = {
                "case_type": case.get("case_type", "unknown"),
                "court_type": case.get("court_type", "unknown"),
                "court_name": case.get("court_name", "unknown"),
                "status": case.get("status", "unknown"),
                "num_hearings": len(hearings),
                "days_pending": days_pending,
                "days_to_hearing": days_to_hearing,
                "avg_hearing_gap": avg_gap,
                "has_advocate": 1 if case.get("advocate_petitioner") else 0,
                "has_subject": 1 if case.get("subject") else 0,
            }
            records.append(record)

        df = pd.DataFrame(records)
        return df

    def _encode_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """Encode categorical features and scale numerical ones."""
        categorical_cols = ["case_type", "court_type", "court_name", "status"]
        numerical_cols = [
            "num_hearings", "days_pending", "days_to_hearing",
            "avg_hearing_gap", "has_advocate", "has_subject",
        ]

        encoded_parts = []

        for col in categorical_cols:
            if col in df.columns:
                if fit or col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    encoded = self.label_encoders[col].fit_transform(
                        df[col].fillna("unknown").astype(str)
                    )
                else:
                    # Handle unseen labels
                    values = df[col].fillna("unknown").astype(str)
                    known = set(self.label_encoders[col].classes_)
                    values = values.apply(lambda x: x if x in known else "unknown")
                    if "unknown" not in known:
                        self.label_encoders[col].classes_ = np.append(
                            self.label_encoders[col].classes_, "unknown"
                        )
                    encoded = self.label_encoders[col].transform(values)
                encoded_parts.append(encoded.reshape(-1, 1))

        num_data = df[numerical_cols].fillna(0).values
        if fit:
            num_data = self.scaler.fit_transform(num_data)
        else:
            num_data = self.scaler.transform(num_data)
        encoded_parts.append(num_data)

        return np.hstack(encoded_parts)

    def train_hearing_model(self, cases: List[Dict], labels: List[int]) -> Dict:
        """
        Train the hearing likelihood prediction model.
        Labels: 1 = hearing will occur, 0 = hearing will be adjourned/cancelled.
        """
        df = self.prepare_features(cases)
        X = self._encode_features(df, fit=True)
        y = np.array(labels)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.hearing_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42,
            class_weight="balanced",
        )
        self.hearing_model.fit(X_train, y_train)  # type: ignore[union-attr]

        # Evaluate
        y_pred = self.hearing_model.predict(X_test)  # type: ignore[union-attr]
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Cross-validation
        cv_scores = cross_val_score(self.hearing_model, X, y, cv=5, scoring="accuracy")  # type: ignore[arg-type]

        self._save_models()

        return {
            "accuracy": round(accuracy, 4),  # type: ignore[call-overload]
            "cv_mean": round(cv_scores.mean(), 4),  # type: ignore[call-overload]
            "cv_std": round(cv_scores.std(), 4),  # type: ignore[call-overload]
            "report": report,
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def train_outcome_model(self, cases: List[Dict], outcomes: List[str]) -> Dict:
        """
        Train case outcome prediction model.
        Outcomes: 'disposed', 'pending', 'settled', etc.
        """
        df = self.prepare_features(cases)
        X = self._encode_features(df, fit=True)

        outcome_encoder = LabelEncoder()
        y = outcome_encoder.fit_transform(outcomes)
        self.label_encoders["outcome"] = outcome_encoder

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.outcome_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42,
        )
        self.outcome_model.fit(X_train, y_train)  # type: ignore[union-attr]

        y_pred = self.outcome_model.predict(X_test)  # type: ignore[union-attr]
        accuracy = accuracy_score(y_test, y_pred)

        self._save_models()

        return {
            "accuracy": round(accuracy, 4),  # type: ignore[call-overload]
            "classes": list(outcome_encoder.classes_),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }

    def predict_hearing(self, case_data: Dict) -> Dict:
        """Predict whether a hearing will occur for a case."""
        if not self.hearing_model:
            return {"error": "Hearing model not trained", "probability": 0.5}

        df = self.prepare_features([case_data])
        X = self._encode_features(df)
        prob = self.hearing_model.predict_proba(X)[0]  # type: ignore[union-attr]
        prediction = self.hearing_model.predict(X)[0]  # type: ignore[union-attr]

        return {
            "will_occur": bool(prediction),
            "probability": round(float(prob[1]), 4),  # type: ignore[call-overload]
            "confidence": "high" if max(prob) > 0.8 else "medium" if max(prob) > 0.6 else "low",
        }

    def predict_outcome(self, case_data: Dict) -> Dict:
        """Predict the likely outcome of a case."""
        if not self.outcome_model:
            return {"error": "Outcome model not trained"}

        df = self.prepare_features([case_data])
        X = self._encode_features(df)
        prob = self.outcome_model.predict_proba(X)[0]  # type: ignore[union-attr]
        prediction = self.outcome_model.predict(X)[0]  # type: ignore[union-attr]

        outcome_encoder = self.label_encoders.get("outcome")
        if outcome_encoder:
            predicted_label = outcome_encoder.inverse_transform([prediction])[0]
            class_probs = {
                label: round(float(p), 4)  # type: ignore[call-overload]
                for label, p in zip(outcome_encoder.classes_, prob)  # type: ignore[union-attr]
            }
        else:
            predicted_label = str(prediction)
            class_probs = {}

        return {
            "predicted_outcome": predicted_label,
            "probability": round(float(max(prob)), 4),  # type: ignore[call-overload]
            "all_probabilities": class_probs,
            "confidence": "high" if max(prob) > 0.7 else "medium" if max(prob) > 0.5 else "low",
        }

    def get_feature_importance(self) -> Dict:
        """Get feature importance from the hearing model."""
        if not self.hearing_model:
            return {"error": "Model not trained"}

        feature_names = [
            "case_type", "court_type", "court_name", "status",
            "num_hearings", "days_pending", "days_to_hearing",
            "avg_hearing_gap", "has_advocate", "has_subject",
        ]
        importances = self.hearing_model.feature_importances_  # type: ignore[union-attr]
        sorted_idx = np.argsort(importances)[::-1]

        return {
            "features": [
                {"name": feature_names[i], "importance": round(float(importances[i]), 4)}  # type: ignore[call-overload]
                for i in sorted_idx
            ]
        }
