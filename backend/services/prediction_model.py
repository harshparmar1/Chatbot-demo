import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import SentenceTransformer

# Try importing XGBoost, otherwise fallback to Scikit-learn Gradient Boosting Regressor
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor
    HAS_XGB = False

class PredictionModelService:
    def __init__(self, models_dir=None):
        if models_dir is None:
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Paths to saved models
        self.risk_model_path = os.path.join(self.models_dir, 'risk_regressor.pkl')
        self.comp_model_path = os.path.join(self.models_dir, 'comp_regressor.pkl')
        self.encoders_path = os.path.join(self.models_dir, 'label_encoders.pkl')
        
        self.embedding_model = None
        self.label_encoders = {}
        self.risk_model = None
        self.comp_model = None
        
        self.load_models()

    def get_embedding_model(self):
        if self.embedding_model is None:
            # Load local SentenceTransformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def load_models(self):
        """
        Load models and encoders if they exist.
        """
        try:
            if os.path.exists(self.encoders_path):
                with open(self.encoders_path, 'rb') as f:
                    self.label_encoders = pickle.load(f)
            
            if os.path.exists(self.risk_model_path):
                with open(self.risk_model_path, 'rb') as f:
                    self.risk_model = pickle.load(f)
                    
            if os.path.exists(self.comp_model_path):
                with open(self.comp_model_path, 'rb') as f:
                    self.comp_model = pickle.load(f)
        except Exception as e:
            print(f"Warning: Failed to load models: {e}. They will be trained dynamically.")

    def save_models(self):
        """
        Persist trained models and encoders.
        """
        try:
            with open(self.encoders_path, 'wb') as f:
                pickle.dump(self.label_encoders, f)
            with open(self.risk_model_path, 'wb') as f:
                pickle.dump(self.risk_model, f)
            with open(self.comp_model_path, 'wb') as f:
                pickle.dump(self.comp_model, f)
            print("ML models successfully saved.")
        except Exception as e:
            print(f"Error saving ML models: {e}")

    def generate_heuristics(self, df):
        """
        Calculate baseline Risk and Compliance scores using intelligent feature engineering rules.
        """
        risk_scores = []
        comp_scores = []
        
        for idx, row in df.iterrows():
            status = str(row['Status']).lower()
            chk = str(row['Checklist Name']).lower()
            rem = str(row['Remarks']).lower()
            
            # Base risk score
            risk = 10.0
            
            # Status impact
            if status == 'fail':
                risk += 60.0
            elif status == 'pending':
                risk += 25.0
            
            # Remarks keyword impact
            negatives = ["expired", "blocked", "fail", "incorrect", "dirty", "violation", "low", "limit", "abnormal", "critical", "not sanitized", "damaged", "overdue", "mixed"]
            positives = ["success", "clean", "comply", "follow", "normal", "acceptable", "well", "no issues", "functioning"]
            
            if any(n in rem for n in negatives):
                risk += 15.0
            elif any(p in rem for p in positives):
                risk -= 10.0
                
            # Checklist risk level
            critical_checklists = ['fire', 'icu', 'theatre', 'oxygen', 'gas', 'ventilator', 'defibrillator', 'emergency']
            if any(c in chk for c in critical_checklists):
                risk += 10.0
                
            # Shift risk (extracted from Created At hour)
            try:
                dt = pd.to_datetime(row['Created At'], format='%d-%m-%Y %H:%M')
                hour = dt.hour
            except Exception:
                hour = 12
                
            # Shift categorization (Morning, Afternoon, Night)
            if 0 <= hour < 7 or 18 <= hour <= 23:
                risk += 5.0  # Night shifts have slightly higher risk
                
            # Add small deterministic noise to make distributions realistic
            h = hash(rem) % 5
            risk += h
            
            # Clamp Risk score 0 - 100
            risk = max(0.0, min(100.0, risk))
            risk_scores.append(risk)
            
            # Compliance: Inversely related to risk
            comp = 100.0 - risk + (hash(rem) % 6 - 3)
            comp = max(0.0, min(100.0, comp))
            comp_scores.append(comp)
            
        return np.array(risk_scores), np.array(comp_scores)

    def extract_datetime_features(self, date_series):
        """
        Extract Year, Month, Weekday, Hour, Shift, Weekend.
        """
        dt_features = []
        for d in date_series:
            try:
                dt = pd.to_datetime(d)
                year = dt.year
                month = dt.month
                weekday = dt.weekday()
                hour = dt.hour
                # Shift: Morning (7-11) = 0, Afternoon (12-17) = 1, Night/Evening (18-6) = 2
                if 7 <= hour <= 11:
                    shift = 0
                elif 12 <= hour <= 17:
                    shift = 1
                else:
                    shift = 2
                weekend = 1 if weekday >= 5 else 0
            except Exception:
                year, month, weekday, hour, shift, weekend = 2025, 6, 0, 12, 1, 0
            dt_features.append([year, month, weekday, hour, shift, weekend])
        return np.array(dt_features)

    def engineer_features(self, df, fit=False):
        """
        Build feature matrix X from input dataframe.
        """
        # Created By Label Encoding
        created_by_col = df['Created By'].fillna('Unknown').astype(str).tolist()
        if fit:
            self.label_encoders['Created By'] = LabelEncoder()
            self.label_encoders['Created By'].fit(created_by_col + ['Unknown'])
        try:
            created_by_enc = self.label_encoders['Created By'].transform(created_by_col)
        except Exception:
            # Handle unseen labels gracefully
            classes = self.label_encoders['Created By'].classes_
            created_by_mapped = [x if x in classes else 'Unknown' for x in created_by_col]
            created_by_enc = self.label_encoders['Created By'].transform(created_by_mapped)

        # Location Label Encoding
        location_col = df['Location'].fillna('Unknown').astype(str).tolist()
        if fit:
            self.label_encoders['Location'] = LabelEncoder()
            self.label_encoders['Location'].fit(location_col + ['Unknown'])
        try:
            location_enc = self.label_encoders['Location'].transform(location_col)
        except Exception:
            classes = self.label_encoders['Location'].classes_
            location_mapped = [x if x in classes else 'Unknown' for x in location_col]
            location_enc = self.label_encoders['Location'].transform(location_mapped)

        # Checklist Name Label Encoding
        checklist_col = df['Checklist Name'].fillna('Unknown').astype(str).tolist()
        if fit:
            self.label_encoders['Checklist Name'] = LabelEncoder()
            self.label_encoders['Checklist Name'].fit(checklist_col + ['Unknown'])
        try:
            checklist_enc = self.label_encoders['Checklist Name'].transform(checklist_col)
        except Exception:
            classes = self.label_encoders['Checklist Name'].classes_
            checklist_mapped = [x if x in classes else 'Unknown' for x in checklist_col]
            checklist_enc = self.label_encoders['Checklist Name'].transform(checklist_mapped)

        # Status: Pass = 0, Pending = 1, Fail = 2
        status_map = {'pass': 0, 'pending': 1, 'fail': 2}
        status_enc = df['Status'].astype(str).str.lower().map(status_map).fillna(1).values

        # Created At datetime components
        dt_features = self.extract_datetime_features(df['Created At'])

        # Remarks sentence transformer embeddings
        remarks_list = df['Remarks'].fillna('').astype(str).tolist()
        emb_model = self.get_embedding_model()
        remarks_embeddings = emb_model.encode(remarks_list, convert_to_numpy=True)

        # Concatenate features
        # Columns: Created By (1), Location (1), Checklist Name (1), Status (1), Datetime (6), Remarks Embeddings (384)
        X = np.hstack([
            created_by_enc.reshape(-1, 1),
            location_enc.reshape(-1, 1),
            checklist_enc.reshape(-1, 1),
            status_enc.reshape(-1, 1),
            dt_features,
            remarks_embeddings
        ])
        
        return X

    def train(self, df):
        """
        Train ML models on the CSV dataset.
        """
        print("Starting ML Model training...")
        
        # 1. Generate ground truth labels via heuristics
        y_risk, y_comp = self.generate_heuristics(df)
        
        # 2. Extract features
        X = self.engineer_features(df, fit=True)
        
        # 3. Instantiate and train regressors
        if HAS_XGB:
            print("Using XGBoost Regressor for training.")
            self.risk_model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
            self.comp_model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        else:
            print("Using GradientBoostingRegressor for training.")
            self.risk_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
            self.comp_model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
            
        self.risk_model.fit(X, y_risk)
        self.comp_model.fit(X, y_comp)
        
        # 4. Save models
        self.save_models()
        print("ML Model training completed successfully!")
        return True

    def predict(self, df):
        """
        Predict risk and compliance scores for a dataframe.
        """
        # If no models are loaded/trained, we train them now!
        if self.risk_model is None or self.comp_model is None:
            self.train(df)
            
        X = self.engineer_features(df, fit=False)
        
        pred_risk = self.risk_model.predict(X)
        pred_comp = self.comp_model.predict(X)
        
        # Clamp predictions to range 0 - 100
        pred_risk = np.clip(pred_risk, 0.0, 100.0)
        pred_comp = np.clip(pred_comp, 0.0, 100.0)
        
        return pred_risk, pred_comp
