from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.core.policies.policy import Policy
from typing import Any, List, Dict, Text
from rasa.engine.util import Fingerprintable

# Register the custom policy
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.POLICY_WITHOUT_END_TO_END_SUPPORT],
    is_trainable=True,
)
class FallbackPolicy(Policy, Fingerprintable):
    def __init__(self, nlu_threshold: float = 0.4, core_threshold: float = 0.3, fallback_action_name: Text = "action_sorry_couldnt_answer"):
        self.nlu_threshold = nlu_threshold
        self.core_threshold = core_threshold
        self.fallback_action_name = fallback_action_name

    def train(self, training_trackers: List, domain: Dict, **kwargs) -> Dict[Text, Any]:
        """Implement training logic if needed."""
        # Return a fingerprintable object
        return {
            "nlu_threshold": self.nlu_threshold,
            "core_threshold": self.core_threshold,
            "fallback_action_name": self.fallback_action_name
        }

    def predict_action_probabilities(self, tracker, domain, **kwargs) -> List[float]:
        """Implement prediction logic"""
        return [0.0] * domain.num_actions

    def fingerprint(self) -> Dict[Text, Any]:
        """Override to provide a fingerprintable object (for caching)."""
        return {
            "nlu_threshold": self.nlu_threshold,
            "core_threshold": self.core_threshold,
            "fallback_action_name": self.fallback_action_name
        }
