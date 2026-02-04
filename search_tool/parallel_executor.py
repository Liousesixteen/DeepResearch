"""
并行执行管理器模块
支持多模型并行调用，提高执行效率
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from models_registry import get_model_registry


@dataclass
class ModelResult:
    """模型执行结果"""
    model_key: str
    model_name: str
    response: str
    execution_time: float
    status: str  # "success", "error", "timeout"
    error_message: Optional[str] = None
    raw_completion: Any = None


class ParallelModelExecutor:
    """并行模型执行器"""
    
    def __init__(self, max_workers: int = 5, timeout: int = 300):
        self.max_workers = max_workers
        self.timeout = timeout
        self.registry = get_model_registry()
        self.results: List[ModelResult] = []
        self.lock = threading.Lock()
        # 添加输出锁，用于同步流式输出
        self.output_lock = threading.Lock()
        # 添加模型输出状态跟踪
        self.model_output_status = {}
    
    def execute_models(self, model_keys: List[str], query: str, 
                      suppress_thinking: bool = True, streaming: bool = True) -> List[ModelResult]:
        """
        并行执行多个模型
        
        Args:
            model_keys: 要执行的模型键列表
            query: 查询问题
            suppress_thinking: 是否抑制thinking过程
            streaming: 是否使用流式响应
            
        Returns:
            执行结果列表
        """
        self.results = []
        print(f"\n🚀 开始并行执行 {len(model_keys)} 个模型...")
        print(f"⏱️  超时设置: {self.timeout}秒")
        print(f"🔇 Thinking抑制: {'开启' if suppress_thinking else '关闭'}")
        print(f"📡 流式响应: {'开启' if streaming else '关闭'}")
        print("-" * 80)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_model = {
                executor.submit(self._execute_single_model, model_key, query, suppress_thinking, streaming): model_key
                for model_key in model_keys
            }
            
            # 收集结果
            completed_count = 0
            for future in as_completed(future_to_model, timeout=self.timeout):
                model_key = future_to_model[future]
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.results.append(result)
                        completed_count += 1
                        print(f"✅ {result.model_name} 执行完成 ({result.execution_time:.2f}s)")
                except TimeoutError:
                    print(f"⏰ {model_key} 执行超时")
                    with self.lock:
                        self.results.append(ModelResult(
                            model_key=model_key,
                            model_name=model_key.replace("_", " ").title(),
                            response="",
                            execution_time=self.timeout,
                            status="timeout",
                            error_message="执行超时"
                        ))
                except Exception as e:
                    print(f"❌ {model_key} 执行失败: {str(e)}")
                    with self.lock:
                        self.results.append(ModelResult(
                            model_key=model_key,
                            model_name=model_key.replace("_", " ").title(),
                            response="",
                            execution_time=0,
                            status="error",
                            error_message=str(e)
                        ))
        
        total_time = time.time() - start_time
        print(f"\n🎯 并行执行完成！")
        print(f"📊 总计: {len(model_keys)} 个模型")
        print(f"✅ 成功: {len([r for r in self.results if r.status == 'success'])} 个")
        print(f"❌ 失败: {len([r for r in self.results if r.status != 'success'])} 个")
        print(f"⏱️  总耗时: {total_time:.2f}秒")
        print("-" * 80)
        
        return self.results
    
    def _execute_single_model(self, model_key: str, query: str, 
                            suppress_thinking: bool, streaming: bool) -> Optional[ModelResult]:
        """执行单个模型"""
        start_time = time.time()
        
        try:
            # 获取模型实例
            model_class = self.registry.get_model_class(model_key)
            if not model_class:
                raise ValueError(f"模型 {model_key} 不存在")
            
            # 获取模型信息
            model_info = self.registry.get_model_info(model_key)
            model_name = model_info.get("name", model_key.replace("_", " ").title())
            
            # 创建模型实例
            model = model_class(self.registry._api_configs)
            
            # 设置模型标识，用于流式输出同步
            if hasattr(model, 'set_output_context'):
                model.set_output_context(self.output_lock, model_name)
            
            # 执行查询
            with self.output_lock:
                print(f"🔄 正在执行 {model_name}...")
            
            response, completion = model.search_with_retry(
                query=query,
                streaming=streaming,
                suppress_thinking=suppress_thinking
            )
            
            if response:
                execution_time = time.time() - start_time
                return ModelResult(
                    model_key=model_key,
                    model_name=model_name,
                    response=response,
                    execution_time=execution_time,
                    status="success",
                    raw_completion=completion
                )
            else:
                raise ValueError("模型返回空响应")
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ModelResult(
                model_key=model_key,
                model_name=model_key.replace("_", " ").title(),
                response="",
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )
    
    def get_successful_results(self) -> List[ModelResult]:
        """获取成功的执行结果"""
        return [r for r in self.results if r.status == "success"]
    
    def get_failed_results(self) -> List[ModelResult]:
        """获取失败的执行结果"""
        return [r for r in self.results if r.status != "success"]
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        total = len(self.results)
        successful = len(self.get_successful_results())
        failed = len(self.get_failed_results())
        
        if successful > 0:
            avg_time = sum(r.execution_time for r in self.get_successful_results()) / successful
            min_time = min(r.execution_time for r in self.get_successful_results())
            max_time = max(r.execution_time for r in self.get_successful_results())
        else:
            avg_time = min_time = max_time = 0
        
        return {
            "total_models": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time
        }
