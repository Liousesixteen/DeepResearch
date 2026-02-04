"""
模型注册表模块
用于管理和注册所有可用的搜索模型
"""

from typing import Dict, List, Optional, Type
try:
    from .models_impl import (
        BaseSearchModel,
        GoogleDeepResearch,
        GoogleDeepResearchPro,
        GrokDeepSearch,
        HunyuanT1,
        HunyuanT1Latest,
        GPTSearch,
        Gemini25FlashAll,
        Gemini25ProAll,
        DeepSeekSearch,
        KimiSearch,
        GPT4Gizmo,
        DeepSeekV3,
        GPT4All,
        GPT4oAll,
        O3DeepResearch20250626,
        O4MiniDeepResearch20250626,
        O4MiniDeepResearch,
        O3DeepResearch
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from models_impl import (
        BaseSearchModel,
        GoogleDeepResearch,
        GoogleDeepResearchPro,
        GrokDeepSearch,
        HunyuanT1,
        HunyuanT1Latest,
        GPTSearch,
        Gemini25FlashAll,
        Gemini25ProAll,
        DeepSeekSearch,
        KimiSearch,
        GPT4Gizmo,
        DeepSeekV3,
        GPT4All,
        GPT4oAll,
        O3DeepResearch20250626,
        O4MiniDeepResearch20250626,
        O4MiniDeepResearch,
        O3DeepResearch
    )


class ModelRegistry:
    """模型注册表类"""
    
    def __init__(self):
        self._models: Dict[str, Type[BaseSearchModel]] = {}
        self._model_info: Dict[str, Dict] = {}
        self._api_configs: Dict[str, str] = {
            "primary_base": "https://yunwu.ai/v1",
            "primary_key": "sk-Al4I3dIn54J7Mxpb6g0aMTJ5QfDQ9elsatmWmKLmjoMGh25J",
            "backup_base": "https://openkey.cloud/v1",
            "backup_key": "sk-JhthldK6DOHIqh7HA29e61451116419aA96d526b22886604"
        }
        self._register_default_models()
    
    def _register_default_models(self):
        """注册默认模型"""
        default_models = {
            "google_deep_research": {
                "class": GoogleDeepResearch,
                "name": "Google Deep Research",
                "description": "Google Gemini 2.5 Flash Deep Search 模型",
                "model_id": "gemini-2.5-flash-deepsearch"
            },
            "google_deep_research_pro": {
                "class": GoogleDeepResearchPro,
                "name": "Google Deep Research Pro",
                "description": "Google Gemini 2.5 Pro Deep Search 模型",
                "model_id": "gemini-2.5-pro-deepsearch"
            },
            "grok_deep_search": {
                "class": GrokDeepSearch,
                "name": "Grok Deep Search",
                "description": "xAI Grok 3 Deep Search 模型",
                "model_id": "grok-3-deepsearch"
            },
            "hunyuan_t1": {
                "class": HunyuanT1,
                "name": "Hunyuan T1 Latest",
                "description": "Hunyuan T1 Latest 模型（可能不带搜索功能）",
                "model_id": "hunyuan-t1-latest"
            },
            "hunyuan_t1_latest": {
                "class": HunyuanT1Latest,
                "name": "Hunyuan T1 Latest",
                "description": "腾讯混元 Hunyuan-T1 大模型 (腾讯元宝-万码云API)",
                "model_id": "hunyuan-t1-latest"
            },
            "gpt_search": {
                "class": GPTSearch,
                "name": "GPT Search",
                "description": "OpenAI GPT-4o Search 模型",
                "model_id": "gpt-4o-search-preview-2025-03-11"
            },
            "gemini_25_flash_all": {
                "class": Gemini25FlashAll,
                "name": "Gemini 2.5 Flash All",
                "description": "Google Gemini 2.5 Flash All 模型",
                "model_id": "gemini-2.5-flash-all"
            },
            "gemini_25_pro_all": {
                "class": Gemini25ProAll,
                "name": "Gemini 2.5 Pro All",
                "description": "Google Gemini 2.5 Pro All 模型",
                "model_id": "gemini-2.5-pro-all"
            },
            "deepseek_search": {
                "class": DeepSeekSearch,
                "name": "DeepSeek Search",
                "description": "DeepSeek R1 Searching 模型",
                "model_id": "deepseek-r1-searching"
            },
            "kimi_search": {
                "class": KimiSearch,
                "name": "Kimi Search",
                "description": "Kimi K2 Search 模型",
                "model_id": "kimi-k2-0711-preview-search"
            },
            "gpt4_gizmo": {
                "class": GPT4Gizmo,
                "name": "GPT-4 Gizmo",
                "description": "OpenAI GPT-4 Gizmo 模型",
                "model_id": "gpt-4-gizmo-*"
            },
            "deepseek_v3": {
                "class": DeepSeekV3,
                "name": "DeepSeek V3",
                "description": "DeepSeek V3 模型",
                "model_id": "deepseek-v3-250324"
            },
            "gpt4_all": {
                "class": GPT4All,
                "name": "GPT-4 All",
                "description": "OpenAI GPT-4 All 模型",
                "model_id": "gpt-4-all"
            },
            "gpt4o_all": {
                "class": GPT4oAll,
                "name": "GPT-4o All",
                "description": "OpenAI GPT-4o All 模型",
                "model_id": "gpt-4o-all"
            },
            "o3_deep_research_20250626": {
                "class": O3DeepResearch20250626,
                "name": "O3 Deep Research 2025-06-26",
                "description": "O3 Deep Research 2025-06-26 模型",
                "model_id": "o3-deep-research-2025-06-26"
            },
            "o4_mini_deep_research_20250626": {
                "class": O4MiniDeepResearch20250626,
                "name": "O4 Mini Deep Research 2025-06-26",
                "description": "云雾平台 O4 Mini Deep Research 2025-06-26 模型",
                "model_id": "o4-mini-deep-research-2025-06-26"
            },
            "o4_mini_deep_research": {
                "class": O4MiniDeepResearch,
                "name": "O4 Mini Deep Research",
                "description": "云雾平台 O4 Mini Deep Research 模型",
                "model_id": "o4-mini-deep-research"
            },
            "o3_deep_research": {
                "class": O3DeepResearch,
                "name": "O3 Deep Research",
                "description": "云雾平台 O3 Deep Research 模型",
                "model_id": "o3-deep-research"
            }
        }
        
        for key, info in default_models.items():
            self.register_model(key, info["class"], info)
    
    def register_model(self, key: str, model_class: Type[BaseSearchModel], info: Dict = None):
        """注册新模型"""
        self._models[key] = model_class
        if info:
            self._model_info[key] = info
        else:
            self._model_info[key] = {
                "name": key.replace("_", " ").title(),
                "description": f"{key} 模型",
                "model_id": key
            }
    
    def unregister_model(self, key: str) -> bool:
        """注销模型"""
        if key in self._models:
            del self._models[key]
            if key in self._model_info:
                del self._model_info[key]
            return True
        return False
    
    def get_model(self, key: str) -> Optional[BaseSearchModel]:
        """获取模型实例"""
        if key in self._models:
            model_class = self._models[key]
            return model_class(self._api_configs)
        return None
    
    def get_model_class(self, key: str) -> Optional[Type[BaseSearchModel]]:
        """获取模型类"""
        return self._models.get(key)
    
    def get_model_info(self, key: str) -> Optional[Dict]:
        """获取模型信息"""
        return self._model_info.get(key)
    
    def list_models(self) -> List[str]:
        """列出所有可用模型"""
        return list(self._models.keys())
    
    def list_model_info(self) -> Dict[str, Dict]:
        """列出所有模型信息"""
        return self._model_info.copy()
    
    def update_api_configs(self, configs: Dict[str, str]):
        """更新API配置"""
        self._api_configs.update(configs)
    
    def get_api_configs(self) -> Dict[str, str]:
        """获取API配置"""
        return self._api_configs.copy()
    
    def is_model_available(self, key: str) -> bool:
        """检查模型是否可用"""
        return key in self._models
    
    def get_model_count(self) -> int:
        """获取模型数量"""
        return len(self._models)


# 全局模型注册表实例
model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    """获取全局模型注册表实例"""
    return model_registry


def register_model(key: str, model_class: Type[BaseSearchModel], info: Dict = None):
    """注册模型的便捷函数"""
    model_registry.register_model(key, model_class, info)


def get_model(key: str) -> Optional[BaseSearchModel]:
    """获取模型的便捷函数"""
    return model_registry.get_model(key)


def list_models() -> List[str]:
    """列出所有模型的便捷函数"""
    return model_registry.list_models()


def list_model_info() -> Dict[str, Dict]:
    """列出所有模型信息的便捷函数"""
    return model_registry.list_model_info()
