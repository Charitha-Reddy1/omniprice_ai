"""
Machine Learning Demand Predictor.
Multi-domain aware demand forecasting trained on combined hotel, product, flight, and travel package data.
Incorporates customer behaviour signals and special events.
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

RANDOM_SEED = 42
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

FEATURE_COLUMNS_NUM = [
    "base_price",
    "current_price",
    "competitor_price",
    "price_ratio",
    "occupancy_rate",
    "inventory_ratio",
    "inventory_remaining",
    "days_remaining",
    "is_weekend",
    "season_multiplier",
    "event_multiplier",
    "booking_velocity",
    "price_sensitivity",
    "purchase_frequency",
]

FEATURE_COLUMNS_CAT = [
    "domain",
    "customer_segment",
    "season",
    "special_event"
]


class DemandPredictor:
    """Multi-domain ML Demand Predictor with customer behaviour and special event awareness."""

    def __init__(self, model_filename="demand_model.pkl", metadata_filename="model_metadata.json"):
        self.model_path = os.path.join(MODEL_DIR, model_filename)
        self.metadata_path = os.path.join(MODEL_DIR, metadata_filename)
        self.pipeline = None
        self.metadata = {}
        self.is_loaded = False
        os.makedirs(MODEL_DIR, exist_ok=True)

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "domain" not in df.columns:
            df["domain"] = "hotel"
        if "price_ratio" not in df.columns:
            df["price_ratio"] = df["competitor_price"] / df["current_price"].replace(0, 1)
        if "is_weekend" not in df.columns:
            df["is_weekend"] = 0
        if "season_multiplier" not in df.columns:
            df["season_multiplier"] = 1.0
        if "event_multiplier" not in df.columns:
            df["event_multiplier"] = 1.0
        if "booking_velocity" not in df.columns:
            df["booking_velocity"] = 2.0
        if "occupancy_rate" not in df.columns:
            df["occupancy_rate"] = 0.5
        if "inventory_ratio" not in df.columns:
            df["inventory_ratio"] = 0.5
        if "days_remaining" not in df.columns:
            df["days_remaining"] = 7
        if "customer_segment" not in df.columns:
            df["customer_segment"] = "Standard"
        if "price_sensitivity" not in df.columns:
            df["price_sensitivity"] = 1.0
        if "purchase_frequency" not in df.columns:
            df["purchase_frequency"] = 2.0
        if "season" not in df.columns:
            df["season"] = "Regular"
        if "special_event" not in df.columns:
            df["special_event"] = "Normal Day"
            
        all_cols = FEATURE_COLUMNS_NUM + FEATURE_COLUMNS_CAT
        for col in all_cols:
            if col not in df.columns:
                if col in FEATURE_COLUMNS_NUM:
                    df[col] = 0.0
                else:
                    df[col] = "Standard"
        return df[all_cols]

    def train_and_save(self, csv_filename="combined_demand_training.csv", model_type="hist_gb"):
        """Train model on multi-domain dataset, compute evaluation metrics, and save to disk."""
        data_path = os.path.join(DATA_DIR, csv_filename)
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"Training dataset not found: {data_path}"
            )

        df = pd.read_csv(data_path)
        X = self._prepare_features(df)
        y = df["demand_score"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=RANDOM_SEED
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", FEATURE_COLUMNS_NUM),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), FEATURE_COLUMNS_CAT),
            ]
        )

        if model_type == "rf":
            regressor = RandomForestRegressor(
                n_estimators=150, max_depth=14, random_state=RANDOM_SEED, n_jobs=-1
            )
        else:
            regressor = HistGradientBoostingRegressor(
                max_iter=200, max_depth=9, learning_rate=0.07, random_state=RANDOM_SEED
            )

        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor)
        ])

        start_time = time.time()
        pipeline.fit(X_train, y_train)
        training_time_sec = round(time.time() - start_time, 4)

        y_pred = pipeline.predict(X_test)
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2 = float(r2_score(y_test, y_pred))

        joblib.dump(pipeline, self.model_path)

        self.metadata = {
            "model_type": model_type,
            "training_dataset": csv_filename,
            "domains": ["hotel", "product", "flight", "travel_package"],
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "random_seed": RANDOM_SEED,
            "sklearn_version": sklearn.__version__,
            "training_time_seconds": training_time_sec,
            "metrics": {
                "mae": round(mae, 3),
                "rmse": round(rmse, 3),
                "r2_score": round(r2, 4)
            },
            "features_numeric": FEATURE_COLUMNS_NUM,
            "features_categorical": FEATURE_COLUMNS_CAT,
            "saved_at_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "status": "trained_and_persisted"
        }

        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

        self.pipeline = pipeline
        self.is_loaded = True
        print(f"[ML Multi-Domain] Model trained & saved to {self.model_path}")
        print(f"[ML Multi-Domain] Real Metrics -> MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.4f}")
        return self.metadata

    def load_model(self):
        """Load trained pipeline and metadata from disk."""
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, "r") as f:
                        self.metadata = json.load(f)
                self.is_loaded = True
                print(f"[ML] Successfully loaded model from {self.model_path}")
                return True
            except Exception as e:
                print(f"[ML Warning] Failed to load model: {e}")
                self.is_loaded = False
        return False

    def predict_demand(self, raw_input: dict) -> dict:
        """
        Perform real inference across any domain (hotel, product, flight, travel_package).
        Returns: predicted demand_score (0-100), confidence_score (0-1), latency_ms.
        """
        start_t = time.perf_counter()
        
        # Ensure model is ready
        if not self.is_loaded or self.pipeline is None:
            loaded = self.load_model()
            if not loaded:
                return self._fallback_prediction(raw_input, start_t)

        try:
            df_in = pd.DataFrame([raw_input])
            X = self._prepare_features(df_in)
            pred = float(self.pipeline.predict(X)[0])
            pred_clamped = float(np.clip(pred, 1.0, 100.0))
            
            # Confidence score calculation
            price_ratio = raw_input.get("competitor_price", 1) / max(raw_input.get("current_price", 1), 1)
            ratio_penalty = abs(price_ratio - 1.0) * 0.12
            r2_base = self.metadata.get("metrics", {}).get("r2_score", 0.94)
            confidence = float(np.clip(r2_base - ratio_penalty, 0.68, 0.98))
            
            latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
            
            return {
                "demand_score": round(pred_clamped, 2),
                "demand_level": self._classify_demand(pred_clamped),
                "confidence_score": round(confidence, 3),
                "prediction_latency_ms": latency_ms,
                "model_version": f"Multi-Domain {self.metadata.get('model_type', 'HistGradientBoosting')}",
                "is_fallback": False
            }
        except Exception as e:
            print(f"[ML Inference Error] {e} -> using fallback")
            return self._fallback_prediction(raw_input, start_t)

    def _classify_demand(self, score: float) -> str:
        if score >= 75:
            return "Very High"
        elif score >= 55:
            return "High"
        elif score >= 40:
            return "Moderate"
        else:
            return "Low"

    def _fallback_prediction(self, raw_input: dict, start_t: float) -> dict:
        base_price = float(raw_input.get("base_price", 5000))
        curr_price = float(raw_input.get("current_price", base_price))
        comp_price = float(raw_input.get("competitor_price", base_price))
        occ_rate = float(raw_input.get("occupancy_rate", 0.5))
        s_mult = float(raw_input.get("season_multiplier", 1.0))
        evt_mult = float(raw_input.get("event_multiplier", 1.0))
        velocity = float(raw_input.get("booking_velocity", 2.0))
        sensitivity = float(raw_input.get("price_sensitivity", 1.0))
        
        ratio = comp_price / max(curr_price, 1.0)
        score = (32.0 + (occ_rate * 28.0) + ((ratio - 1.0) * 22.0) + (s_mult - 1.0) * 18.0 
                 + (evt_mult - 1.0) * 20.0 + (velocity * 1.8) - (sensitivity * 5.0))
        score = float(np.clip(score, 5.0, 95.0))
        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
        
        return {
            "demand_score": round(score, 2),
            "demand_level": self._classify_demand(score),
            "confidence_score": 0.72,
            "prediction_latency_ms": latency_ms,
            "model_version": "Multi-Domain Heuristic Fallback",
            "is_fallback": True
        }


# Global instance
demand_predictor = DemandPredictor()

if __name__ == "__main__":
    demand_predictor.train_and_save("combined_demand_training.csv", model_type="hist_gb")
