#!/usr/bin/env python3
"""
预构建快表系统
在后台预先构建模型可用性快表，避免用户等待时的检测
"""

import time
import threading
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class ModelStatus(Enum):
    """模型状态枚举"""
    UNKNOWN = "unknown"      # 未知状态
    AVAILABLE = "available"  # 可用
    UNAVAILABLE = "unavailable"  # 不可用
    TESTING = "testing"      # 正在测试中

@dataclass
class ModelInfo:
    """模型信息"""
    model_key: str
    status: ModelStatus
    last_test_time: float
    response_time: float
    test_count: int
    success_rate: float
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    stability_score: float = 0.0  # 稳定性评分

class PrebuiltFastTable:
    """预构建快表系统"""
    
    def __init__(self, cache_file: str = "model_availability_cache.json"):
        self.cache_file = Path(cache_file)
        self.model_cache: Dict[str, ModelInfo] = {}
        self.last_full_update: float = 0
        self.lock = threading.Lock()
        
        # 初始化模型状态（纯手动模式，无自动更新）
        self._init_model_cache()
    
    def _init_model_cache(self):
        """初始化模型缓存（纯手动模式）"""
        from models_registry import list_models
        
        models = list_models()
        
        # 尝试从文件加载缓存
        cache_loaded = self._load_cache_from_file()
        
        if not cache_loaded:
            # 初始化所有模型为未知状态
            for model_key in models:
                self.model_cache[model_key] = ModelInfo(
                    model_key=model_key,
                    status=ModelStatus.UNKNOWN,
                    last_test_time=0,
                    response_time=0,
                    test_count=0,
                    success_rate=0.0,
                    last_success_time=None,
                    last_failure_time=None,
                    stability_score=0.0
                )
        
        # 纯手动模式：不启动任何后台更新
        # 快表完全由用户通过 build_fast_table.py 手动维护
    
    def _load_cache_from_file(self) -> bool:
        """从文件加载缓存"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 恢复模型状态
                for model_key, info_data in data.items():
                    # 转换状态枚举
                    status_str = info_data.get('status', 'unknown')
                    try:
                        status = ModelStatus(status_str)
                    except ValueError:
                        status = ModelStatus.UNKNOWN
                    
                    self.model_cache[model_key] = ModelInfo(
                        model_key=model_key,
                        status=status,
                        last_test_time=info_data.get('last_test_time', 0),
                        response_time=info_data.get('response_time', 0),
                        test_count=info_data.get('test_count', 0),
                        success_rate=info_data.get('success_rate', 0.0),
                        last_success_time=info_data.get('last_success_time'),
                        last_failure_time=info_data.get('last_failure_time'),
                        stability_score=info_data.get('stability_score', 0.0)
                    )
                return True
        except Exception as e:
            print(f"⚠️  加载缓存文件失败: {str(e)}")
        
        return False
    
    def _save_cache_to_file(self):
        """保存缓存到文件"""
        try:
            with self.lock:
                cache_data = {}
                for model_key, info in self.model_cache.items():
                    # 转换枚举为字符串
                    info_dict = asdict(info)
                    info_dict['status'] = info.status.value
                    cache_data[model_key] = info_dict
                
                # 确保目录存在
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
                # 静默保存，不打印信息
        except Exception as e:
            # 静默处理错误，不干扰用户
            pass
    
    # 移除后台更新功能，改为纯手动模式
    
    def _should_update_cache(self) -> bool:
        """判断是否需要更新缓存（纯手动模式）"""
        # 纯手动模式：永远不自动更新
        # 快表完全由用户手动维护
        return False
    
    def _update_all_models_background(self):
        """后台更新所有模型状态（已移除，改为纯手动模式）"""
        # 此方法已移除，改为纯手动模式
        # 用户可以通过 build_fast_table.py 手动更新快表
        pass
    
    def _update_stability_score(self, model_key: str):
        """更新模型稳定性评分"""
        info = self.model_cache[model_key]
        
        # 基于成功率和测试次数计算稳定性
        if info.test_count > 0:
            # 基础分数：成功率
            base_score = info.success_rate
            
            # 测试次数奖励：测试次数越多，分数越高
            test_count_bonus = min(0.2, info.test_count * 0.01)
            
            # 最近成功奖励：最近成功的模型分数更高
            recency_bonus = 0
            if info.last_success_time:
                hours_since_success = (time.time() - info.last_success_time) / 3600
                if hours_since_success < 1:  # 1小时内成功
                    recency_bonus = 0.3
                elif hours_since_success < 6:  # 6小时内成功
                    recency_bonus = 0.2
                elif hours_since_success < 24:  # 24小时内成功
                    recency_bonus = 0.1
            
            # 响应时间奖励：响应时间越短，分数越高
            response_time_bonus = 0
            if info.response_time > 0:
                if info.response_time < 5:  # 5秒内响应
                    response_time_bonus = 0.2
                elif info.response_time < 10:  # 10秒内响应
                    response_time_bonus = 0.1
            
            # 计算最终稳定性评分
            stability_score = base_score + test_count_bonus + recency_bonus + response_time_bonus
            info.stability_score = min(1.0, stability_score)
    
    def get_available_models(self, exclude_keys: set = None, min_count: int = 3) -> List[Tuple[str, float]]:
        """
        获取可用的模型列表（按稳定性评分排序，纯手动模式）
        
        Args:
            exclude_keys: 要排除的模型键
            min_count: 最少需要的可用模型数量
            
        Returns:
            List[Tuple[model_key, stability_score]]
        """
        if exclude_keys is None:
            exclude_keys = set()
        
        with self.lock:
            # 获取可用的模型（纯手动模式，不检查过期时间）
            available_models = []
            for model_key, info in self.model_cache.items():
                if (model_key not in exclude_keys and 
                    info.status == ModelStatus.AVAILABLE):
                    available_models.append((model_key, info.stability_score))
            
            # 按稳定性评分排序
            available_models.sort(key=lambda x: x[1], reverse=True)
            
            # 如果可用模型不足，返回所有可用的
            if len(available_models) < min_count:
                print(f"⚠️  可用模型不足，只有 {len(available_models)} 个")
            
            return available_models
    
    def get_cache_status(self) -> Dict:
        """获取缓存状态统计（纯手动模式）"""
        with self.lock:
            total_models = len(self.model_cache)
            
            status_counts = {
                ModelStatus.AVAILABLE: 0,
                ModelStatus.UNAVAILABLE: 0,
                ModelStatus.UNKNOWN: 0,
                ModelStatus.TESTING: 0
            }
            
            for info in self.model_cache.values():
                status_counts[info.status] += 1
            
            return {
                "total_models": total_models,
                "status_counts": {k.value: v for k, v in status_counts.items()},
                "expired_count": 0,  # 纯手动模式，无过期概念
                "last_update": self.last_full_update,
                "cache_age": 0  # 纯手动模式，无缓存年龄概念
            }
    
    def force_update(self):
        """强制更新快表"""
        print("🔄 强制更新快表...")
        self.last_full_update = 0  # 重置更新时间，强制更新
        self._update_all_models_background()
        self._save_cache_to_file()
    
    def clear_cache(self):
        """清空缓存"""
        with self.lock:
            current_time = time.time()
            for info in self.model_cache.values():
                info.status = ModelStatus.UNKNOWN
                info.last_test_time = 0
                info.response_time = 0
                info.test_count = 0
                info.success_rate = 0.0
                info.last_success_time = None
                info.last_failure_time = None
                info.stability_score = 0.0
            
            self.last_full_update = 0
            print("🧹 快表缓存已清空")
    
    def stop_background_update(self):
        """停止后台更新（纯手动模式，无后台更新）"""
        # 纯手动模式：无后台更新线程
        pass

# 全局预构建快表实例
_global_prebuilt_fast_table = None
_prebuilt_fast_table_lock = threading.Lock()

def get_global_prebuilt_fast_table() -> PrebuiltFastTable:
    """获取全局预构建快表实例"""
    global _global_prebuilt_fast_table
    
    if _global_prebuilt_fast_table is None:
        with _prebuilt_fast_table_lock:
            if _global_prebuilt_fast_table is None:
                _global_prebuilt_fast_table = PrebuiltFastTable()
    
    return _global_prebuilt_fast_table

def reset_global_prebuilt_fast_table():
    """重置全局预构建快表实例"""
    global _global_prebuilt_fast_table
    with _prebuilt_fast_table_lock:
        if _global_prebuilt_fast_table:
            _global_prebuilt_fast_table.stop_background_update()
        _global_prebuilt_fast_table = None

