#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能模型选择器
根据用户问题自动选择最合适的搜索模型
"""

import re
from typing import Dict, List, Tuple, Optional
from models_registry import get_model_registry, list_model_info


class SmartModelSelector:
    """智能模型选择器"""
    
    def __init__(self):
        self.registry = get_model_registry()
        self.model_info = list_model_info()
        
        # 定义模型特征和适用场景
        self.model_features = {
            "google_deep_research": {
                "keywords": ["google", "gemini", "搜索", "研究", "深度", "专业"],
                "strengths": ["搜索能力强", "信息准确", "适合研究类问题"],
                "best_for": ["学术研究", "技术问题", "深度分析", "信息搜索"]
            },
            "google_deep_research_pro": {
                "keywords": ["google", "gemini", "pro", "专业", "高级", "复杂"],
                "strengths": ["处理复杂问题", "深度分析", "专业领域"],
                "best_for": ["复杂分析", "专业研究", "深度思考", "技术难题"]
            },
            "grok_deep_search": {
                "keywords": ["grok", "xai", "创新", "创意", "思维", "推理"],
                "strengths": ["创新思维", "逻辑推理", "创意生成"],
                "best_for": ["创意问题", "逻辑推理", "创新思考", "思维训练"]
            },
            "hunyuan_t1": {
                "keywords": ["中文", "混元", "腾讯", "本地化", "中文理解"],
                "strengths": ["中文理解强", "本地化知识", "中文表达"],
                "best_for": ["中文问题", "本地化内容", "中文表达", "中国文化"]
            },
            "hunyuan_t1_latest": {
                "keywords": ["中文", "混元", "腾讯", "最新", "万码云", "增强"],
                "strengths": ["最新中文模型", "搜索增强", "万码云API"],
                "best_for": ["最新中文问题", "搜索增强", "中文深度搜索"]
            },
            "gpt_search": {
                "keywords": ["openai", "gpt", "搜索", "通用", "平衡"],
                "strengths": ["通用性强", "搜索平衡", "稳定性好"],
                "best_for": ["通用问题", "平衡搜索", "稳定回答", "日常查询"]
            },
            "gemini_25_flash_all": {
                "keywords": ["google", "gemini", "flash", "快速", "高效"],
                "strengths": ["响应快速", "效率高", "多模态"],
                "best_for": ["快速回答", "效率优先", "多模态内容", "实时查询"]
            },
            "gemini_25_pro_all": {
                "keywords": ["google", "gemini", "pro", "专业", "全面"],
                "strengths": ["专业全面", "深度理解", "多领域"],
                "best_for": ["专业问题", "全面分析", "多领域", "深度理解"]
            },
            "deepseek_search": {
                "keywords": ["deepseek", "搜索", "专业", "技术", "代码"],
                "strengths": ["技术专业", "代码理解", "搜索精准"],
                "best_for": ["技术问题", "代码相关", "专业搜索", "技术分析"]
            },
            "kimi_search": {
                "keywords": ["kimi", "搜索", "快速", "准确", "中文友好"],
                "strengths": ["中文友好", "搜索快速", "准确度高"],
                "best_for": ["中文搜索", "快速查询", "准确信息", "日常问题"]
            },
            "gpt4_gizmo": {
                "keywords": ["gpt4", "gizmo", "工具", "功能", "实用"],
                "strengths": ["工具使用", "功能丰富", "实用性强"],
                "best_for": ["工具使用", "功能问题", "实用查询", "操作指导"]
            },
            "deepseek_v3": {
                "keywords": ["deepseek", "v3", "最新", "先进", "技术"],
                "strengths": ["最新技术", "先进算法", "性能优秀"],
                "best_for": ["最新技术", "先进问题", "性能要求", "前沿研究"]
            },
            "gpt4_all": {
                "keywords": ["gpt4", "全面", "通用", "稳定", "可靠"],
                "strengths": ["全面通用", "稳定可靠", "质量高"],
                "best_for": ["全面问题", "通用查询", "稳定回答", "高质量"]
            },
            "gpt4o_all": {
                "keywords": ["gpt4o", "最新", "openai", "先进", "多模态"],
                "strengths": ["最新模型", "多模态", "先进技术"],
                "best_for": ["最新问题", "多模态", "先进技术", "创新应用"]
            },
            "o3_deep_research_20250626": {
                "keywords": ["o3", "云雾", "深度研究", "专业", "搜索"],
                "strengths": ["专业搜索", "深度研究", "云雾平台"],
                "best_for": ["专业研究", "深度搜索", "云雾平台", "专业分析"]
            },
            "o4_mini_deep_research_20250626": {
                "keywords": ["o4", "mini", "云雾", "快速", "轻量"],
                "strengths": ["快速响应", "轻量级", "效率高"],
                "best_for": ["快速查询", "轻量问题", "效率优先", "简单搜索"]
            },
            "o4_mini_deep_research": {
                "keywords": ["o4", "mini", "云雾", "标准", "平衡"],
                "strengths": ["平衡性能", "标准质量", "稳定可靠"],
                "best_for": ["标准问题", "平衡性能", "稳定查询", "日常使用"]
            },
            "o3_deep_research": {
                "keywords": ["o3", "云雾", "深度", "研究", "专业"],
                "strengths": ["专业深度", "研究能力", "高质量"],
                "best_for": ["专业研究", "深度分析", "高质量", "学术问题"]
            }
        }
    
    def analyze_query(self, query: str) -> Dict[str, float]:
        """分析查询内容，计算每个模型的匹配分数"""
        query_lower = query.lower()
        scores = {}
        
        for model_key, features in self.model_features.items():
            score = 0.0
            
            # 关键词匹配
            for keyword in features["keywords"]:
                if keyword.lower() in query_lower:
                    score += 2.0
            
            # 问题类型匹配
            question_type = self._detect_question_type(query)
            if question_type in features["best_for"]:
                score += 3.0
            
            # 语言偏好
            if self._is_chinese_query(query):
                if any(lang in features["keywords"] for lang in ["中文", "混元", "腾讯", "kimi"]):
                    score += 2.0
            else:
                if any(lang in features["keywords"] for lang in ["google", "gpt", "openai", "deepseek"]):
                    score += 1.0
            
            # 复杂度评估
            complexity = self._assess_complexity(query)
            if complexity == "high" and "pro" in model_key.lower():
                score += 1.5
            elif complexity == "low" and "mini" in model_key.lower():
                score += 1.0
            
            scores[model_key] = score
        
        return scores
    
    def _detect_question_type(self, query: str) -> str:
        """检测问题类型"""
        query_lower = query.lower()
        
        # 技术问题
        if any(word in query_lower for word in ["代码", "编程", "技术", "算法", "开发", "软件"]):
            return "技术问题"
        
        # 学术研究
        if any(word in query_lower for word in ["研究", "学术", "论文", "理论", "分析", "探讨"]):
            return "学术研究"
        
        # 创意问题
        if any(word in query_lower for word in ["创意", "想法", "建议", "方案", "设计", "创新"]):
            return "创意问题"
        
        # 日常查询
        if any(word in query_lower for word in ["是什么", "怎么", "如何", "为什么", "哪里", "什么时候"]):
            return "日常查询"
        
        # 搜索查询
        if any(word in query_lower for word in ["搜索", "查找", "了解", "信息", "资料"]):
            return "信息搜索"
        
        return "通用问题"
    
    def _is_chinese_query(self, query: str) -> bool:
        """判断是否为中文查询"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', query))
        return chinese_chars > len(query) * 0.3
    
    def _assess_complexity(self, query: str) -> str:
        """评估问题复杂度"""
        query_length = len(query)
        word_count = len(query.split())
        
        if query_length > 100 or word_count > 20:
            return "high"
        elif query_length < 30 or word_count < 5:
            return "low"
        else:
            return "medium"
    
    def select_best_model(self, query: str, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
        """选择最佳模型"""
        scores = self.analyze_query(query)
        
        # 按分数排序
        sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前top_k个模型
        results = []
        for model_key, score in sorted_models[:top_k]:
            info = self.model_info.get(model_key, {})
            results.append((model_key, score, info))
        
        return results

    def select_models_by_threshold(self, query: str, threshold_percent: float = 70.0) -> List[Tuple[str, float, Dict]]:
        """按相对百分比阈值选择多个合适模型。

        计算方式：以本次查询的最高分为100%，其余模型按 (score / max_score * 100) 归一化，
        选择归一化分数 ≥ threshold_percent 的模型。
        若最高分为0（无明显匹配），回退为返回前1名。
        """
        scores = self.analyze_query(query)
        if not scores:
            return []

        # 取最大分数作为基准
        max_score = max(scores.values()) if scores else 0.0
        if max_score <= 0.0:
            # 无有效分数，回退到单模型
            best = self.select_best_model(query, top_k=1)
            # 将原分数映射为100%
            mapped = []
            for model_key, score, info in best:
                mapped.append((model_key, 100.0, info))
            return mapped

        # 归一化并过滤
        normalized: List[Tuple[str, float, Dict]] = []
        for model_key, score in scores.items():
            percent = (score / max_score) * 100.0
            if percent >= threshold_percent:
                info = self.model_info.get(model_key, {})
                normalized.append((model_key, percent, info))

        # 按百分比降序
        normalized.sort(key=lambda x: x[1], reverse=True)
        # 如果过滤后为空，至少保底一个最佳模型
        if not normalized:
            best = self.select_best_model(query, top_k=1)
            fallback = []
            for model_key, score, info in best:
                fallback.append((model_key, 100.0, info))
            return fallback

        return normalized
    
    def explain_selection(self, query: str, selected_model: str) -> str:
        """解释为什么选择这个模型"""
        features = self.model_features.get(selected_model, {})
        question_type = self._detect_question_type(query)
        
        explanation = f"我选择了 {selected_model} 模型，因为：\n"
        explanation += f"1. 问题类型：{question_type}\n"
        explanation += f"2. 模型优势：{', '.join(features.get('strengths', []))}\n"
        explanation += f"3. 适用场景：{', '.join(features.get('best_for', []))}\n"
        
        return explanation


# 全局实例
smart_selector = SmartModelSelector()


def get_smart_selector() -> SmartModelSelector:
    """获取智能选择器实例"""
    return smart_selector


def select_model_for_query(query: str, top_k: int = 3) -> List[Tuple[str, float, Dict]]:
    """为查询选择模型的便捷函数"""
    return smart_selector.select_best_model(query, top_k)

def select_models_for_query_by_threshold(query: str, threshold_percent: float = 70.0) -> List[Tuple[str, float, Dict]]:
    """按相对百分比阈值选择模型的便捷函数（返回列表: (model_key, percent, info)）。"""
    return smart_selector.select_models_by_threshold(query, threshold_percent)


def explain_model_selection(query: str, model_key: str) -> str:
    """解释模型选择的便捷函数"""
    return smart_selector.explain_selection(query, model_key)
