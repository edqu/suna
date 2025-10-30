"""
Models API

Endpoints for listing and managing AI models available to users.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import httpx
import asyncio

from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger
from core.utils.model_selector import model_selector
from core.services.supabase import DBConnection
from core.utils.config import config

router = APIRouter(tags=["models"])

# Cache for Ollama tags - 60 second TTL
_ollama_cache: Dict[str, Any] = {"tags": None, "timestamp": 0}

async def get_ollama_status() -> Dict[str, Any]:
    """
    Get Ollama server status and installed models.
    Returns dict with 'available' (bool) and 'models' (set of model names).
    Cached for 60 seconds.
    """
    import time
    
    # Check cache
    now = time.time()
    if _ollama_cache["tags"] is not None and (now - _ollama_cache["timestamp"]) < 60:
        return _ollama_cache["tags"]
    
    result = {"available": False, "models": set()}
    
    ollama_base = getattr(config, 'OLLAMA_API_BASE', None)
    if not ollama_base:
        _ollama_cache["tags"] = result
        _ollama_cache["timestamp"] = now
        return result
    
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(f"{ollama_base}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                # Extract model names (strip version tags)
                model_names = set()
                for model in models:
                    name = model.get("name", "")
                    # Handle both "llama3:instruct" and "llama3"
                    model_names.add(name)
                    # Also add without tag
                    if ":" in name:
                        model_names.add(name.split(":")[0])
                
                result = {"available": True, "models": model_names}
                logger.debug(f"Ollama status: {len(model_names)} models available")
    except Exception as e:
        logger.debug(f"Ollama not available: {e}")
    
    # Update cache
    _ollama_cache["tags"] = result
    _ollama_cache["timestamp"] = now
    
    return result


class ModelInfo(BaseModel):
    """Response model for individual model information."""
    id: str
    name: str
    provider: str
    context_window: int
    max_output_tokens: Optional[int] = None
    capabilities: List[str]
    pricing: Optional[Dict[str, float]] = None
    enabled: bool
    beta: bool
    tier_availability: List[str]
    priority: int
    recommended: bool
    status: Optional[str] = None  # "installed", "not_installed", "server_down", "remote"


class ModelsListResponse(BaseModel):
    """Response model for list of available models."""
    models: List[ModelInfo]
    default_model: str
    user_tier: str


class ModelsByProviderResponse(BaseModel):
    """Response model for models grouped by provider."""
    providers: Dict[str, List[ModelInfo]]
    default_model: str
    user_tier: str


class ModelValidationRequest(BaseModel):
    """Request model for validating a model ID."""
    model_id: str


class ModelValidationResponse(BaseModel):
    """Response model for model validation."""
    is_valid: bool
    error_message: Optional[str] = None
    model_info: Optional[ModelInfo] = None


@router.get("/models", response_model=ModelsListResponse, summary="List Available Models", operation_id="list_models")
async def list_models(
    tier: Optional[str] = None,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    List all AI models available to the current user based on their subscription tier.
    
    Returns models with pricing, capabilities, and availability information.
    Includes Ollama model status (installed/not_installed/server_down).
    """
    try:
        db = DBConnection()
        client = await db.client
        
        # Get available models for user
        models = await model_selector.get_available_models(client, user_id, include_disabled=False)
        
        # Get Ollama status for local models
        ollama_status = await get_ollama_status()
        
        # Add status to models
        for model in models:
            provider = model.get("provider", "").lower()
            if provider == "ollama":
                if not ollama_status["available"]:
                    model["status"] = "server_down"
                else:
                    # Extract model name from ID (e.g., "ollama/llama3:instruct" -> "llama3:instruct")
                    model_name = model["id"].replace("ollama/", "")
                    is_installed = model_name in ollama_status["models"]
                    model["status"] = "installed" if is_installed else "not_installed"
            else:
                model["status"] = "remote"
        
        # Get default model
        default_model = await model_selector.get_default_model(client, user_id)
        
        # Determine user tier
        from core.billing.subscription_service import subscription_service
        from core.utils.config import config, EnvMode
        
        user_tier = "free"
        if config.ENV_MODE == EnvMode.LOCAL:
            user_tier = "local"
        else:
            try:
                subscription_info = await subscription_service.get_subscription(user_id)
                subscription = subscription_info.get('subscription')
                if subscription:
                    tier_info = subscription_info.get('tier', {})
                    if tier_info and tier_info.get('name') not in ['free', 'none']:
                        user_tier = tier_info.get('name', 'free')
            except Exception as e:
                logger.warning(f"Could not determine user tier: {e}")
        
        return ModelsListResponse(
            models=models,
            default_model=default_model,
            user_tier=user_tier
        )
        
    except Exception as e:
        logger.error(f"Error listing models for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/models/by-provider", response_model=ModelsByProviderResponse, summary="List Models By Provider", operation_id="list_models_by_provider")
async def list_models_by_provider(
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    List available models grouped by provider for easier UI display.
    
    Returns a dictionary mapping provider names (e.g., 'anthropic', 'openai', 'ollama')
    to lists of their respective models.
    """
    try:
        db = DBConnection()
        client = await db.client
        
        # Get available models for user
        models = await model_selector.get_available_models(client, user_id, include_disabled=False)
        
        # Group by provider
        grouped = model_selector.group_models_by_provider(models)
        
        # Get default model
        default_model = await model_selector.get_default_model(client, user_id)
        
        # Determine user tier
        from core.billing.subscription_service import subscription_service
        from core.utils.config import config, EnvMode
        
        user_tier = "free"
        if config.ENV_MODE == EnvMode.LOCAL:
            user_tier = "local"
        else:
            try:
                subscription_info = await subscription_service.get_subscription(user_id)
                subscription = subscription_info.get('subscription')
                if subscription:
                    tier_info = subscription_info.get('tier', {})
                    if tier_info and tier_info.get('name') not in ['free', 'none']:
                        user_tier = tier_info.get('name', 'free')
            except Exception as e:
                logger.warning(f"Could not determine user tier: {e}")
        
        return ModelsByProviderResponse(
            providers=grouped,
            default_model=default_model,
            user_tier=user_tier
        )
        
    except Exception as e:
        logger.error(f"Error listing models by provider for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/models/{model_id}", response_model=ModelInfo, summary="Get Model Info", operation_id="get_model_info")
async def get_model_info(
    model_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    Get detailed information about a specific model.
    
    Returns model capabilities, pricing, context window, and other metadata.
    """
    try:
        model_info = model_selector.get_model_info(model_id)
        
        if not model_info:
            raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
        
        # Verify user has access to this model
        db = DBConnection()
        client = await db.client
        
        is_valid, error_msg = await model_selector.validate_model_for_user(client, user_id, model_id)
        
        if not is_valid:
            raise HTTPException(status_code=403, detail=error_msg)
        
        return model_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model info for {model_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.post("/models/validate", response_model=ModelValidationResponse, summary="Validate Model", operation_id="validate_model")
async def validate_model(
    request: ModelValidationRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    Validate that a model ID is valid and available to the current user.
    
    Returns validation status and model information if valid.
    """
    try:
        db = DBConnection()
        client = await db.client
        
        # Validate model for user
        is_valid, error_msg = await model_selector.validate_model_for_user(
            client, user_id, request.model_id
        )
        
        model_info = None
        if is_valid:
            model_info = model_selector.get_model_info(request.model_id)
        
        return ModelValidationResponse(
            is_valid=is_valid,
            error_message=error_msg if not is_valid else None,
            model_info=model_info if is_valid else None
        )
        
    except Exception as e:
        logger.error(f"Error validating model {request.model_id}: {e}")
        return ModelValidationResponse(
            is_valid=False,
            error_message=f"Validation error: {str(e)}"
        )
