class PredictionService:
    def predict_incident_risk(self, features: dict):
        return {"risk": 0.5, "label": "medium"}
