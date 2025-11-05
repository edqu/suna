"""
Embedding Models API

Endpoints for listing and managing embedding models.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger
from core.ai_models.embedding_models import embedding_registry, get_embedding_model


router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class EmbeddingModelInfo(BaseModel):
    """Response model for embedding model information."""
    id: str
    name: str
    provider: str
    dimensions: int
    max_input_tokens: int
    cost_per_million_tokens: float
    is_local: bool
    requires_api_key: bool
    recommended: bool
    tier_availability: List[str]


class EmbeddingModelsListResponse(BaseModel):
    """Response model for list of embedding models."""
    models: List[Dict[str, Any]]
    default_model: str
    total_count: int


@router.get("/models", response_model=EmbeddingModelsListResponse, summary="List Embedding Models", operation_id="list_embedding_models")
async def list_embedding_models(
    provider: Optional[str] = Query(None, description="Filter by provider (openai, google, ollama, sentence_transformers)"),
    free_only: bool = Query(False, description="Show only free models"),
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """
    List all available embedding models.
    
    Returns models with pricing, dimensions, and provider information.
    Includes both cloud-based and local embedding models.
    """
    try:
        # Get all models
        models = embedding_registry.get_all(enabled_only=True)
        
        # Filter by provider if specified
        if provider:
            from core.ai_models.embedding_models import EmbeddingProvider
            try:
                provider_enum = EmbeddingProvider(provider.lower())
                models = [m for m in models if m.provider == provider_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        # Filter free only if requested
        if free_only:
            models = [m for m in models if m.pricing.cost_per_million_tokens == 0.00]
        
        # Get default model
        default_model = embedding_registry.get_default_model()
        default_model_id = default_model.id if default_model else ""
        
        # Format models for response
        models_data = [model.to_dict() for model in models]
        
        return EmbeddingModelsListResponse(
            models=models_data,
            default_model=default_model_id,
            total_count=len(models_data)
        )
        
    except Exception as e:
        logger.error(f"Error listing embedding models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list embedding models: {str(e)}")


@router.get("/models/{model_id}", summary="Get Embedding Model Info", operation_id="get_embedding_model_info")
async def get_embedding_model_info(
    model_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
) -> Dict[str, Any]:
    """Get detailed information about a specific embedding model."""
    try:
        model = embedding_registry.get(model_id)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Embedding model '{model_id}' not found")
        
        return model.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting embedding model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/default", summary="Get Default Embedding Model", operation_id="get_default_embedding_model")
async def get_default_embedding_model(
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
) -> Dict[str, Any]:
    """Get the default embedding model for the current configuration."""
    try:
        default_model = embedding_registry.get_default_model()
        
        if not default_model:
            raise HTTPException(
                status_code=404,
                detail="No embedding models available. Please configure GEMINI_API_KEY, OPENAI_API_KEY, or OLLAMA_API_BASE."
            )
        
        return {
            **default_model.to_dict(),
            "is_default": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting default embedding model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
