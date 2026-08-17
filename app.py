"""
Main Flask Web Application Entrypoint for Dynamic Pricing Engine.
Loads trained ML models on startup and serves the dashboard and REST APIs.
"""

import os
from flask import Flask, render_template
from routes.api import api_bp
from services.demand_predictor import demand_predictor

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Register API routes
app.register_blueprint(api_bp)


@app.route("/")
def index():
    """Serves the project landing page."""
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    """Serves the main real-time dynamic pricing dashboard."""
    return render_template("dashboard.html")


def init_app():
    """Load trained model and train it from the existing dataset if necessary."""
    print("=" * 60)
    print("  AI-POWERED DYNAMIC PRICING ENGINE - HACKATHON SERVER")
    print("=" * 60)

    # Load ML Demand Model
    loaded = demand_predictor.load_model()

    if not loaded:
        print("[Startup] Model not found on disk.")
        print("[Startup] Training model using existing historical dataset...")

        demand_predictor.train_and_save(
            "combined_demand_training.csv",
            model_type="hist_gb"
        )

    print("[Startup] System initialized and ready for real-time inference.")
    print("=" * 60)


# Load the already-trained model
demand_predictor.load_model()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)