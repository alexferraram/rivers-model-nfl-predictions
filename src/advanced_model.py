"""
Advanced NFL Prediction Model

This module contains enhanced machine learning models for NFL game prediction
with support for complex features including matchups, player stats, injuries, etc.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, RFE
import joblib
import logging
from typing import Dict, Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class AdvancedNFLPredictionModel:
    """Advanced machine learning model for NFL game outcome prediction."""
    
    def __init__(self, model_type: str = 'random_forest', use_feature_selection: bool = True):
        """
        Initialize the advanced prediction model.
        
        Args:
            model_type: Type of model to use
            use_feature_selection: Whether to use feature selection
        """
        self.model_type = model_type
        self.model = None
        self.scaler = RobustScaler()  # More robust to outliers
        self.feature_selector = None
        self.feature_columns = None
        self.selected_features = None
        self.is_trained = False
        self.use_feature_selection = use_feature_selection
        
        # Initialize model based on type
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model based on type."""
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        elif self.model_type == 'extra_trees':
            self.model = ExtraTreesClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
        elif self.model_type == 'neural_network':
            self.model = MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=1000,
                random_state=42
            )
        elif self.model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42,
                class_weight='balanced'
            )
        elif self.model_type == 'logistic_regression':
            self.model = LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced',
                solver='liblinear'
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict:
        """
        Train the advanced model with feature selection and optimization.
        
        Args:
            X: Feature matrix
            y: Target variable
            test_size: Proportion of data to use for testing
            
        Returns:
            Dictionary containing training results
        """
        logger.info(f"Training advanced {self.model_type} model...")
        
        # Store feature columns
        self.feature_columns = list(X.columns)
        
        # Split data with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Feature selection
        if self.use_feature_selection and len(X.columns) > 50:
            logger.info("Performing feature selection...")
            self._perform_feature_selection(X_train, y_train)
            X_train = X_train[self.selected_features]
            X_test = X_test[self.selected_features]
            logger.info(f"Selected {len(self.selected_features)} features from {len(self.feature_columns)}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation with stratified folds
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
        cv_auc_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
        
        results = {
            'accuracy': accuracy,
            'auc_score': auc_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_auc_mean': cv_auc_scores.mean(),
            'cv_auc_std': cv_auc_scores.std(),
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'feature_importance': self._get_feature_importance(),
            'selected_features': self.selected_features,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'y_test': y_test
        }
        
        self.is_trained = True
        logger.info(f"Advanced model training complete. Accuracy: {accuracy:.3f}, AUC: {auc_score:.3f}")
        
        return results
    
    def _perform_feature_selection(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Perform feature selection using multiple methods."""
        # Use SelectKBest with f_classif
        k_best = SelectKBest(score_func=f_classif, k=min(50, len(X_train.columns)))
        k_best.fit(X_train, y_train)
        
        # Get top features
        feature_scores = pd.DataFrame({
            'feature': X_train.columns,
            'score': k_best.scores_
        }).sort_values('score', ascending=False)
        
        # Select top features
        self.selected_features = feature_scores.head(50)['feature'].tolist()
        
        # Store feature selector for later use
        self.feature_selector = k_best
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Apply feature selection if used
        if self.use_feature_selection and self.selected_features:
            X = X[self.selected_features]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return predictions, probabilities
    
    def predict_game_advanced(self, home_team_data: Dict, away_team_data: Dict) -> Dict:
        """
        Predict game outcome with advanced team data.
        
        Args:
            home_team_data: Dictionary of home team comprehensive statistics
            away_team_data: Dictionary of away team comprehensive statistics
            
        Returns:
            Dictionary with detailed prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create comprehensive feature vector
        features = {}
        
        # Add home team features
        for key, value in home_team_data.items():
            if isinstance(value, (int, float)):
                features[f'home_{key}'] = value
        
        # Add away team features
        for key, value in away_team_data.items():
            if isinstance(value, (int, float)):
                features[f'away_{key}'] = value
        
        # Add differential features
        for key in home_team_data.keys():
            if key in away_team_data and isinstance(home_team_data[key], (int, float)):
                features[f'{key}_diff'] = home_team_data[key] - away_team_data[key]
        
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Ensure all required features are present
        required_features = self.selected_features if self.selected_features else self.feature_columns
        for col in required_features:
            if col not in feature_df.columns:
                feature_df[col] = 0
        
        # Reorder columns to match training data
        feature_df = feature_df[required_features]
        
        # Make prediction
        prediction, probability = self.predict(feature_df)
        
        # Calculate confidence and additional metrics
        confidence = max(probability[0], 1 - probability[0])
        
        # Determine key factors
        key_factors = self._analyze_key_factors(home_team_data, away_team_data, feature_df)
        
        return {
            'home_win_probability': probability[0],
            'away_win_probability': 1 - probability[0],
            'predicted_winner': 'home' if prediction[0] == 1 else 'away',
            'confidence': confidence,
            'key_factors': key_factors,
            'feature_contributions': self._get_feature_contributions(feature_df)
        }
    
    def _analyze_key_factors(self, home_data: Dict, away_data: Dict, features: pd.DataFrame) -> List[str]:
        """Analyze key factors influencing the prediction."""
        factors = []
        
        # Check important differentials
        important_diffs = [
            'yards_per_play_diff', 'third_down_rate_diff', 'redzone_td_rate_diff',
            'turnover_rate_diff', 'passing_yards_per_game_diff', 'touchdowns_per_game_diff'
        ]
        
        for diff in important_diffs:
            if diff in features.columns:
                value = features[diff].iloc[0]
                if abs(value) > 0.1:  # Significant difference
                    if value > 0:
                        factors.append(f"Home team advantage in {diff.replace('_diff', '')}")
                    else:
                        factors.append(f"Away team advantage in {diff.replace('_diff', '')}")
        
        # Check injury impact
        if 'home_injury_key_injury_rate' in features.columns and 'away_injury_key_injury_rate' in features.columns:
            home_injuries = features['home_injury_key_injury_rate'].iloc[0]
            away_injuries = features['away_injury_key_injury_rate'].iloc[0]
            
            if home_injuries > away_injuries + 0.1:
                factors.append("Away team has fewer key player injuries")
            elif away_injuries > home_injuries + 0.1:
                factors.append("Home team has fewer key player injuries")
        
        return factors[:5]  # Return top 5 factors
    
    def _get_feature_contributions(self, features: pd.DataFrame) -> Dict[str, float]:
        """Get feature contributions to the prediction."""
        if not hasattr(self.model, 'feature_importances_'):
            return {}
        
        contributions = {}
        feature_names = self.selected_features if self.selected_features else self.feature_columns
        
        for i, feature in enumerate(feature_names):
            if i < len(self.model.feature_importances_):
                contributions[feature] = self.model.feature_importances_[i]
        
        return dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_trained:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.selected_features if self.selected_features else self.feature_columns
            importance_dict = dict(zip(feature_names, self.model.feature_importances_))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        else:
            return {}
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Optimize hyperparameters using grid search.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Dictionary with optimization results
        """
        logger.info("Optimizing hyperparameters...")
        
        # Define parameter grids for different models
        param_grids = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'gradient_boosting': {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1],
                'max_depth': [6, 8, 10],
                'min_samples_split': [2, 5, 10]
            },
            'extra_trees': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'neural_network': {
                'hidden_layer_sizes': [(50,), (100,), (100, 50), (100, 50, 25)],
                'activation': ['relu', 'tanh'],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate': ['constant', 'adaptive']
            },
            'svm': {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
                'kernel': ['rbf', 'poly']
            },
            'logistic_regression': {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        }
        
        if self.model_type not in param_grids:
            raise ValueError(f"Hyperparameter optimization not supported for {self.model_type}")
        
        # Perform grid search with stratified CV
        grid_search = GridSearchCV(
            self.model, param_grids[self.model_type], 
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
            scoring='roc_auc', n_jobs=-1, verbose=1
        )
        
        # Apply feature selection if used
        if self.use_feature_selection and len(X.columns) > 50:
            self._perform_feature_selection(X, y)
            X_selected = X[self.selected_features]
        else:
            X_selected = X
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_selected)
        
        grid_search.fit(X_scaled, y)
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
        
        logger.info(f"Hyperparameter optimization complete. Best score: {grid_search.best_score_:.3f}")
        
        return results
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'feature_columns': self.feature_columns,
            'selected_features': self.selected_features,
            'model_type': self.model_type,
            'use_feature_selection': self.use_feature_selection,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Advanced model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_selector = model_data['feature_selector']
        self.feature_columns = model_data['feature_columns']
        self.selected_features = model_data['selected_features']
        self.model_type = model_data['model_type']
        self.use_feature_selection = model_data['use_feature_selection']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Advanced model loaded from {filepath}")
    
    def get_model_summary(self) -> Dict:
        """Get a summary of the model."""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'total_features': len(self.feature_columns) if self.feature_columns else 0,
            'selected_features': len(self.selected_features) if self.selected_features else 0,
            'use_feature_selection': self.use_feature_selection,
            'feature_importance': self._get_feature_importance()
        }






