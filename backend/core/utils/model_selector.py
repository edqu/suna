"""
Model Selection Utility

Provides functionality for selecting and validating AI models for agents.
Supports listing available models based on user tier and validating model choices.
"""

from typing import Optional, List, Dict, Any
from core.ai_models import model_manager
from core.utils.logger import logger


class ModelSelector:
    """Utility class for selecting and managing AI models for agents."""
    
    @staticmethod
    async def get_available_models(client, user_id: str, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of available models for a user based on their subscription tier.
        
        Args:
            client: Database client
            user_id: User ID
            include_disabled: Whether to include disabled models
            
        Returns:
            List of model information dictionaries
        """
        try:
            from core.billing.subscription_service import subscription_service
            from core.utils.config import config, EnvMode
            
            # In local mode, show all models
            if config.ENV_MODE == EnvMode.LOCAL:
                logger.debug(f"Local mode: returning all available models")
                return model_manager.list_available_models(tier=None, include_disabled=include_disabled)
            
            # Get user's subscription tier
            subscription_info = await subscription_service.get_subscription(user_id)
            subscription = subscription_info.get('subscription')
            
            tier_name = "free"
            if subscription:
                tier_info = subscription_info.get('tier', {})
                if tier_info and tier_info.get('name') != 'free' and tier_info.get('name') != 'none':
                    tier_name = "paid"
            
            logger.debug(f"User {user_id} tier: {tier_name}")
            
            # Get models for user's tier
            models = model_manager.list_available_models(tier=tier_name, include_disabled=include_disabled)
            
            return models
            
        except Exception as e:
            logger.warning(f"Error getting available models for user {user_id}: {e}")
            # Return free tier models as fallback
            return model_manager.list_available_models(tier="free", include_disabled=False)
    
    @staticmethod
    async def get_default_model(client, user_id: str) -> str:
        """
        Get the default model for a user based on their subscription tier.
        
        Args:
            client: Database client
            user_id: User ID
            
        Returns:
            Model ID string
        """
        return await model_manager.get_default_model_for_user(client, user_id)
    
    @staticmethod
    def validate_model(model_id: str) -> tuple[bool, str]:
        """
        Validate that a model ID is valid and enabled.
        
        Args:
            model_id: Model ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not model_id:
            return False, "Model ID cannot be empty"
        
        # Validate model exists and is enabled
        is_valid, error_msg = model_manager.validate_model(model_id)
        
        if not is_valid:
            logger.warning(f"Model validation failed for '{model_id}': {error_msg}")
            return False, error_msg
        
        return True, ""
    
    @staticmethod
    async def validate_model_for_user(client, user_id: str, model_id: str) -> tuple[bool, str]:
        """
        Validate that a model is available to a specific user based on their tier.
        
        Args:
            client: Database client
            user_id: User ID
            model_id: Model ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        from core.utils.config import config, EnvMode
        
        # Basic validation first
        is_valid, error_msg = ModelSelector.validate_model(model_id)
        if not is_valid:
            return False, error_msg
        
        # In local mode, allow all valid models
        if config.ENV_MODE == EnvMode.LOCAL:
            return True, ""
        
        # Get user's available models
        try:
            available_models = await ModelSelector.get_available_models(client, user_id, include_disabled=False)
            available_model_ids = [m['id'] for m in available_models]
            
            # Resolve the model ID in case it's an alias
            resolved_model_id = model_manager.resolve_model_id(model_id)
            
            if resolved_model_id not in available_model_ids:
                return False, f"Model '{model_id}' is not available for your subscription tier"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating model for user {user_id}: {e}")
            return False, f"Failed to validate model availability: {str(e)}"
    
    @staticmethod
    def get_model_info(model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model information dictionary or None if not found
        """
        try:
            return model_manager.format_model_info(model_id)
        except Exception as e:
            logger.error(f"Error getting model info for '{model_id}': {e}")
            return None
    
    @staticmethod
    def list_all_models(tier: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available models, optionally filtered by tier.
        
        Args:
            tier: Subscription tier to filter by ('free', 'paid', or None for all)
            
        Returns:
            List of model information dictionaries
        """
        return model_manager.list_available_models(tier=tier, include_disabled=False)
    
    @staticmethod
    def group_models_by_provider(models: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group models by their provider for easier UI display.
        
        Args:
            models: List of model dictionaries
            
        Returns:
            Dictionary mapping provider names to lists of models
        """
        grouped = {}
        for model in models:
            provider = model.get('provider', 'unknown')
            if provider not in grouped:
                grouped[provider] = []
            grouped[provider].append(model)
        
        return grouped


# Convenience instance for importing
model_selector = ModelSelector()
