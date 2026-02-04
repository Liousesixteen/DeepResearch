"""
联网搜索工具包
提供统一的AI模型联网搜索功能
"""

__version__ = "1.0.0"
__author__ = "Search Tool Team"

from .models_registry import (
    get_model_registry,
    register_model,
    get_model,
    list_models,
    list_model_info
)

from .models_impl import (
    BaseSearchModel,
    GoogleDeepResearch,
    GoogleDeepResearchPro,
    GPTSearch,
    DeepSeekSearch,
    GrokDeepSearch,
    KimiSearch,
    GPT4Gizmo,
    DeepSeekV3,
    GPT4All,
    GPT4oAll,
    Gemini25FlashAll,
    Gemini25ProAll
)

__all__ = [
    "get_model_registry",
    "register_model", 
    "get_model",
    "list_models",
    "list_model_info",
    "BaseSearchModel",
    "GoogleDeepResearch",
    "GoogleDeepResearchPro",
    "GPTSearch",
    "DeepSeekSearch",
    "GrokDeepSearch",
    "KimiSearch",
    "GPT4Gizmo",
    "DeepSeekV3"
]
