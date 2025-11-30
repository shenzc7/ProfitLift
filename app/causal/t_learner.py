from sklearn.ensemble import RandomForestClassifier
import numpy as np
from typing import Tuple, Optional
import logging


class TLearner:
    """T-Learner: train separate models for control and treatment groups."""

    def __init__(self, n_estimators: int = 20, random_state: int = 42):
        """
        Initialize T-Learner with RandomForest models.

        Args:
            n_estimators: Number of trees in RandomForest
            random_state: Random seed for reproducibility
        """
        self.control_model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.treatment_model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state
        )
        self.is_fitted = False
        self.logger = logging.getLogger(__name__)

    def fit(self, X_control: np.ndarray, y_control: np.ndarray,
            X_treatment: np.ndarray, y_treatment: np.ndarray):
        """
        Train separate models for control and treatment groups.

        Args:
            X_control: Features for control group (didn't buy antecedent)
            y_control: Outcomes for control group (didn't buy consequent)
            X_treatment: Features for treatment group (did buy antecedent)
            y_treatment: Outcomes for treatment group (did buy consequent)
        """
        try:
            self.control_model.fit(X_control, y_control)
            self.treatment_model.fit(X_treatment, y_treatment)
            self.is_fitted = True
            self.logger.debug("T-Learner fitted successfully")
        except Exception as e:
            self.logger.error(f"Error fitting T-Learner: {e}")
            self.is_fitted = False
            raise

    def predict_uplift(self, X: np.ndarray) -> np.ndarray:
        """
        Predict uplift: τ(x) = P(Y=1|T=1,X) - P(Y=1|T=0,X)

        Args:
            X: Feature matrix for prediction

        Returns:
            Uplift estimates for each sample
        """
        if not self.is_fitted:
            raise ValueError("T-Learner must be fitted before prediction")

        try:
            # Predict probabilities for treatment and control outcomes
            p_treatment = self.treatment_model.predict_proba(X)[:, 1]
            p_control = self.control_model.predict_proba(X)[:, 1]

            # Calculate uplift
            uplift = p_treatment - p_control

            return uplift

        except Exception as e:
            self.logger.error(f"Error predicting uplift: {e}")
            raise

    def predict_treatment_probability(self, X: np.ndarray) -> np.ndarray:
        """Predict probability of positive outcome under treatment."""
        if not self.is_fitted:
            raise ValueError("T-Learner must be fitted before prediction")
        return self.treatment_model.predict_proba(X)[:, 1]

    def predict_control_probability(self, X: np.ndarray) -> np.ndarray:
        """Predict probability of positive outcome under control."""
        if not self.is_fitted:
            raise ValueError("T-Learner must be fitted before prediction")
        return self.control_model.predict_proba(X)[:, 1]
