"""
联网搜索模型实现模块
包含各种AI模型的联网搜索调用逻辑
"""

import openai
import time
import threading
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any, Dict


class BaseSearchModel(ABC):
    """搜索模型基类"""
    
    def __init__(self, model_name: str, api_configs: Dict[str, str]):
        self.model_name = model_name
        self.api_configs = api_configs
        
        # API配置 - 使用正确的键名
        self.primary_api = {
            "base": "https://yunwu.ai/v1",
            "key": api_configs.get("primary_key", "")
        }
        self.backup_api = {
            "base": "https://openkey.cloud/v1", 
            "key": api_configs.get("backup_key", "")
        }
        
        # 输出同步相关属性
        self.output_lock = None
        self.model_display_name = None
        self.is_parallel_mode = False
    
    def _setup_api_config(self, use_primary: bool = True):
        """设置API配置"""
        if use_primary:
            openai.api_base = self.primary_api["base"]
            openai.api_key = self.primary_api["key"]
        else:
            openai.api_base = self.backup_api["base"]
            openai.api_key = self.backup_api["key"]
    
    def _process_streaming_response(self, completion, suppress_thinking: bool = False) -> Tuple[str, Any]:
        """处理流式响应"""
        msg = ""
        thinking_content = ""
        final_content = ""
        in_thinking = False
        
        # 显示开始回答的标识
        if self.is_parallel_mode:
            self._safe_print(f"\n[{self.model_display_name}] 开始回答：")
        else:
            print(f"\n🚀 {self.model_name} 开始回答：")
        
        try:
            for chunk in completion:
                # 安全检查：确保chunk有choices属性且不为空
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and choice.delta:
                        raw = choice.delta.get('content', '')
                        if raw:
                            msg += raw
                            text = raw
                            printable_total = ""
                            # 显式解析 <think> 标签，支持同一chunk内多段
                            while text:
                                start_idx = text.find("<think>")
                                end_idx = text.find("</think>")
                                if start_idx == -1 and end_idx == -1:
                                    # 无标签，整段属于当前状态
                                    segment = text
                                    text = ""
                                else:
                                    # 取最近的标签位置
                                    cut_idx = min([i for i in [start_idx, end_idx] if i != -1])
                                    segment = text[:cut_idx]
                                    text = text[cut_idx:]
                                # 先处理当前段的可打印性
                                if segment:
                                    if in_thinking and suppress_thinking:
                                        pass  # 丢弃思维段内容
                                    else:
                                        final_content += segment
                                        printable_total += segment
                                # 处理标签并推进状态
                                if text.startswith("<think>"):
                                    in_thinking = True
                                    thinking_content += "<think>"
                                    text = text[len("<think>"):]
                                elif text.startswith("</think>"):
                                    thinking_content += "</think>"
                                    in_thinking = False
                                    text = text[len("</think>"):]
                            if printable_total:
                                print(printable_total, end="", flush=True)
                # 如果chunk没有choices，可能是万码云API的特殊格式
                elif hasattr(chunk, 'content'):
                    raw = chunk.content
                    if raw:
                        msg += raw
                        text = raw
                        printable_total = ""
                        while text:
                            start_idx = text.find("<think>")
                            end_idx = text.find("</think>")
                            if start_idx == -1 and end_idx == -1:
                                segment = text
                                text = ""
                            else:
                                cut_idx = min([i for i in [start_idx, end_idx] if i != -1])
                                segment = text[:cut_idx]
                                text = text[cut_idx:]
                            if segment:
                                if in_thinking and suppress_thinking:
                                    pass
                                else:
                                    final_content += segment
                                    printable_total += segment
                            if text.startswith("<think>"):
                                in_thinking = True
                                thinking_content += "<think>"
                                text = text[len("<think>"):]
                            elif text.startswith("</think>"):
                                thinking_content += "</think>"
                                in_thinking = False
                                text = text[len("</think>"):]
                        if printable_total:
                            print(printable_total, end="", flush=True)
        except Exception as e:
            error_msg = f"\n⚠️ 处理流式响应时出错: {e}"
            if self.is_parallel_mode:
                self._safe_print(error_msg)
            else:
                print(error_msg)
            # 如果流式处理失败，尝试从completion中提取内容
            try:
                if hasattr(completion, 'choices') and completion.choices:
                    msg = completion.choices[0].message.get('content', '')
                elif hasattr(completion, 'content'):
                    msg = completion.content
            except:
                pass
        
        # 流式输出结束后添加换行
        print()  # 添加换行
        
        # 不额外打印换行，保持输出由上层统一控制
        
        # 如果启用了thinking抑制，返回最终内容；否则返回完整内容
        if suppress_thinking and final_content:
            return final_content, completion
        return msg, completion
    
    def set_output_context(self, output_lock: threading.Lock, model_display_name: str):
        """设置输出上下文，用于并行执行时的输出同步"""
        self.output_lock = output_lock
        self.model_display_name = model_display_name
        self.is_parallel_mode = True
    
    def _safe_print(self, content: str, end: str = "", flush: bool = True):
        """安全的打印方法，支持并行输出同步"""
        if self.is_parallel_mode and self.output_lock:
            with self.output_lock:
                print(f"[{self.model_display_name}] {content}", end=end, flush=flush)
        else:
            print(content, end=end, flush=flush)
    
    def _safe_print_status(self, content: str, end: str = "\n", flush: bool = True):
        """安全的打印状态信息，用于API调用状态等"""
        if self.is_parallel_mode and self.output_lock:
            with self.output_lock:
                print(f"[{self.model_display_name}] {content}", end=end, flush=flush)
        else:
            print(content, end=end, flush=flush)
    
    def _is_thinking_content(self, content: str) -> bool:
        """检测是否为thinking内容"""
        thinking_indicators = [
            "让我思考一下", "让我想想", "我来分析一下", "让我研究一下",
            "让我搜索一下", "我来查找", "让我探索", "我来研究",
            "Let me think", "Let me search", "Let me analyze", "Let me explore",
            "I'll think about", "I'll search for", "I'll analyze", "I'll explore",
            "思考中", "分析中", "搜索中", "研究中",
            "Thinking", "Analyzing", "Searching", "Researching"
        ]
        
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in thinking_indicators)
    
    def _extract_final_answer(self, full_response: str) -> str:
        """从完整响应中提取最终答案"""
        # 移除thinking相关内容
        thinking_patterns = [
            r"让我思考一下.*?",
            r"让我想想.*?",
            r"我来分析一下.*?",
            r"让我研究一下.*?",
            r"Let me think.*?",
            r"Let me search.*?",
            r"Let me analyze.*?",
            r"思考中.*?",
            r"分析中.*?",
            r"搜索中.*?"
        ]
        
        import re
        result = full_response
        for pattern in thinking_patterns:
            result = re.sub(pattern, "", result, flags=re.DOTALL | re.IGNORECASE)
        
        # 清理多余的空行和空格
        result = re.sub(r'\n\s*\n', '\n\n', result)
        result = result.strip()
        
        return result if result else full_response
    
    def _handle_api_error(self, err: Exception, attempt: int, max_retries: int) -> Tuple[bool, str]:
        """统一的错误处理方法"""
        error_msg = str(err)
        error_type = type(err).__name__
        
        # 检查是否需要重试
        if 'RateLimitError' in error_type or '负载已饱和' in error_msg or 'overloaded' in error_msg.lower():
            if attempt == 0:
                return True, "切换到备用API"
            else:
                return False, "所有API提供商都遇到负载问题"
        
        # 其他错误类型
        if attempt < max_retries:
            return True, "普通错误，准备重试"
        else:
            return False, f"达到最大重试次数: {error_msg}"
    
    def search_with_retry(self, query: str, streaming: bool = True, model_display_name: str = None, 
                         temperature: float = None, max_tokens: int = None, request_timeout: int = None,
                         suppress_thinking: bool = False) -> Tuple[Optional[str], Any]:
        """统一的搜索重试方法，支持自定义参数"""
        if model_display_name is None:
            model_display_name = self.model_name
            
        # 使用默认参数或自定义参数
        temp = temperature if temperature is not None else 0.7
        tokens = max_tokens if max_tokens is not None else 3000
        timeout = request_timeout if request_timeout is not None else 150
            
        # 主API重试3次
        for attempt in range(3):
            try:
                self._setup_api_config(use_primary=True)
                
                start_time = time.time()
                self._safe_print_status(f"尝试调用 {model_display_name} API (尝试 {attempt + 1}/3, 主API)")
                self._safe_print_status(f"API Base: {openai.api_base}")
                self._safe_print_status(f"Model: {self.model_name}")
                # print(f"参数: temperature={temp}, max_tokens={tokens}")

                completion = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': query}],
                    stream=streaming,
                    temperature=temp,
                    max_tokens=tokens,
                    request_timeout=timeout
                )
                msg = None

                if streaming:
                    msg, completion = self._process_streaming_response(completion, suppress_thinking)
                else:
                    if not completion.choices:
                        raise ValueError("No choices returned from API.")
                    msg = completion.choices[0].message['content']
                    if suppress_thinking and msg:
                        msg = self._extract_final_answer(msg)

                if msg:
                    end_time = time.time()
                    self._safe_print_status(f"耗时: {end_time - start_time:.2f} 秒")
                    # 在并行模式下不重复打印回答内容，因为流式输出已经显示了
                    if not self.is_parallel_mode:
                        self._safe_print_status(f"回答内容: {msg}")
                    return msg, completion
                else:
                    raise ValueError("No valid response received from API")

            except Exception as err:
                self._safe_print_status(f"API Error: {str(err)}")
                self._safe_print_status(f"Error type: {type(err).__name__}")
                
                if attempt < 2:  # 前两次重试
                    self._safe_print_status(f"🔄 准备重试... (尝试 {attempt + 2}/3)")
                    time.sleep(2 ** (attempt + 2))
                    continue
                else:  # 第3次失败后切换到备用API
                    self._safe_print_status("⚠️ 检测到主API暂时不可用")
                    self._safe_print_status("🔄 尝试切换到备用 API...")
                    break
        
        # 备用API重试3次
        self._safe_print_status("🔄 已切换到备用API，准备重试...")
        for attempt in range(3):
            try:
                self._setup_api_config(use_primary=False)
                
                start_time = time.time()
                self._safe_print_status(f"尝试调用 {model_display_name} API (尝试 {attempt + 1}/3, 备用API)")
                self._safe_print_status(f"API Base: {openai.api_base}")
                self._safe_print_status(f"Model: {self.model_name}")
                # print(f"参数: temperature={temp}, max_tokens={tokens}")

                completion = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': query}],
                    stream=streaming,
                    temperature=temp,
                    max_tokens=tokens,
                    request_timeout=timeout
                )
                msg = None

                if streaming:
                    msg, completion = self._process_streaming_response(completion, suppress_thinking)
                else:
                    if not completion.choices:
                        raise ValueError("No choices returned from API.")
                    msg = completion.choices[0].message['content']
                    if suppress_thinking and msg:
                        msg = self._extract_final_answer(msg)

                if msg:
                    end_time = time.time()
                    self._safe_print_status(f"耗时: {end_time - start_time:.2f} 秒")
                    # 在并行模式下不重复打印回答内容，因为流式输出已经显示了
                    if not self.is_parallel_mode:
                        self._safe_print_status(f"回答内容: {msg}")
                    return msg, completion
                else:
                    raise ValueError("No valid response received from API")

            except Exception as err:
                self._safe_print_status(f"API Error: {str(err)}")
                self._safe_print_status(f"Error type: {type(err).__name__}")
                
                if attempt < 2:  # 前两次重试
                    self._safe_print_status(f"🔄 准备重试... (尝试 {attempt + 2}/3)")
                    time.sleep(2 ** (attempt + 2))
                    continue
                else:  # 第3次失败
                    self._safe_print_status("⚠️ 检测到备用API暂时不可用")
                    break
        
        self._safe_print_status("❌ 所有 API 都暂时不可用")
        self._safe_print_status(f"❌ {model_display_name} 调用失败，未获得有效响应")
        self._safe_print_status("可能的原因：")
        self._safe_print_status("1. 服务器负载过高")
        self._safe_print_status("2. 模型暂时不可用")
        self._safe_print_status("3. 网络连接问题")
        self._safe_print_status("4. API Key 问题")
        return None, None



    @abstractmethod
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """搜索方法 - 子类必须实现"""
        pass


class GoogleDeepResearch(BaseSearchModel):
    """Google Deep Research 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gemini-2.5-flash-deepsearch", api_configs)
        # 自定义参数
        self.temperature = 0.7
        self.max_tokens = 3000
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Google Deep Research 模型"""
        return self.search_with_retry(
            query, streaming, "Google Deep Research",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GoogleDeepResearchPro(BaseSearchModel):
    """Google Deep Research Pro 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gemini-2.5-pro-deepsearch", api_configs)
        # 自定义参数 - Pro版本使用更保守的参数
        self.temperature = 0.7
        self.max_tokens = 4000
        self.request_timeout = 180
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Google Deep Research Pro 模型"""
        return self.search_with_retry(
            query, streaming, "Google Deep Research Pro",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GPTSearch(BaseSearchModel):
    """GPT Search 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gpt-4o-search-preview-2025-03-11", api_configs)
        # 自定义参数 - GPT Search优化参数
        self.temperature = 0.7
        self.max_tokens = 3500
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 GPT Search 模型"""
        return self.search_with_retry(
            query, streaming, "GPT Search",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class DeepSeekSearch(BaseSearchModel):
    """DeepSeek Search 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("deepseek-r1-searching", api_configs)
        # 自定义参数 - DeepSeek搜索优化
        self.temperature = 0.7
        self.max_tokens = 3200
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 DeepSeek Search 模型"""
        return self.search_with_retry(
            query, streaming, "DeepSeek Search",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GrokDeepSearch(BaseSearchModel):
    """Grok Deep Search 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("grok-3-deepsearch", api_configs)
        # 自定义参数 - Grok搜索优化
        self.temperature = 0.7
        self.max_tokens = 2800
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Grok Deep Search 模型"""
        return self.search_with_retry(
            query, streaming, "Grok Deep Search",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class KimiSearch(BaseSearchModel):
    """Kimi Search 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("kimi-k2-0711-preview-search", api_configs)
        # 自定义参数 - Kimi搜索优化
        self.temperature = 0.7
        self.max_tokens = 3000
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Kimi Search 模型"""
        return self.search_with_retry(
            query, streaming, "Kimi Search",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GPT4Gizmo(BaseSearchModel):
    """GPT-4 Gizmo 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gpt-4-gizmo-*", api_configs)
        # 自定义参数 - Gizmo优化
        self.temperature = 0.7
        self.max_tokens = 2500
        self.request_timeout = 100
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 GPT-4 Gizmo 模型"""
        return self.search_with_retry(
            query, streaming, "GPT-4 Gizmo",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class DeepSeekV3(BaseSearchModel):
    """DeepSeek V3 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("deepseek-v3-250324", api_configs)
        # 自定义参数 - DeepSeek V3优化
        self.temperature = 0.7
        self.max_tokens = 3500
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 DeepSeek V3 模型"""
        return self.search_with_retry(
            query, streaming, "DeepSeek V3",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GPT4All(BaseSearchModel):
    """GPT-4 All 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gpt-4-all", api_configs)
        # 自定义参数 - GPT-4 All优化
        self.temperature = 0.7
        self.max_tokens = 3000
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 GPT-4 All 模型"""
        return self.search_with_retry(
            query, streaming, "GPT-4 All",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class GPT4oAll(BaseSearchModel):
    """GPT-4o All 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gpt-4o-all", api_configs)
        # 自定义参数 - GPT-4o All优化
        self.temperature = 0.7
        self.max_tokens = 3200
        self.request_timeout = 100
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 GPT-4o All 模型"""
        return self.search_with_retry(
            query, streaming, "GPT-4o All",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class Gemini25FlashAll(BaseSearchModel):
    """Gemini 2.5 Flash All 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gemini-2.5-flash-all", api_configs)
        # 自定义参数 - Gemini Flash优化
        self.temperature = 0.7
        self.max_tokens = 2800
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Gemini 2.5 Flash All 模型"""
        return self.search_with_retry(
            query, streaming, "Gemini 2.5 Flash All",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class Gemini25ProAll(BaseSearchModel):
    """Gemini 2.5 Pro All 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gemini-2.5-pro-all", api_configs)
        # 自定义参数 - Gemini Pro优化
        self.temperature = 0.7
        self.max_tokens = 4000
        self.request_timeout = 180
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Gemini 2.5 Pro All 模型"""
        return self.search_with_retry(
            query, streaming, "Gemini 2.5 Pro All",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class O3DeepResearch20250626(BaseSearchModel):
    """O3 Deep Research 2025-06-26 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("o3-deep-research-2025-06-26", api_configs)
        # 自定义参数 - O3 Deep Research优化
        self.temperature = 0.7
        self.max_tokens = 3500
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 O3 Deep Research 2025-06-26 模型"""
        return self.search_with_retry(
            query, streaming, "O3 Deep Research 2025-06-26",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class O3DeepResearch(BaseSearchModel):
    """O3 Deep Research 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("o3-deep-research", api_configs)
        # 自定义参数 - O3 Deep Research优化
        self.temperature = 0.7
        self.max_tokens = 3500
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 O3 Deep Research 模型"""
        return self.search_with_retry(
            query, streaming, "O3 Deep Research",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class O4MiniDeepResearch20250626(BaseSearchModel):
    """O4 Mini Deep Research 2025-06-26 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("o4-mini-deep-research-2025-06-26", api_configs)
        # 自定义参数 - O4 Mini优化
        self.temperature = 0.7
        self.max_tokens = 2500
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 O4 Mini Deep Research 2025-06-26 模型"""
        return self.search_with_retry(
            query, streaming, "O4 Mini Deep Research 2025-06-26",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class O4MiniDeepResearch(BaseSearchModel):
    """O4 Mini Deep Research 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("o4-mini-deep-research", api_configs)
        # 自定义参数 - O4 Mini优化
        self.temperature = 0.7
        self.max_tokens = 2500
        self.request_timeout = 120
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 O4 Mini Deep Research 模型"""
        return self.search_with_retry(
            query, streaming, "O4 Mini Deep Research",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class HunyuanT1(BaseSearchModel):
    """Hunyuan T1 模型"""
    
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("hunyuan-t1-latest", api_configs)
        # 自定义参数 - Hunyuan T1优化
        self.temperature = 0.7
        self.max_tokens = 3000
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Hunyuan T1 模型"""
        return self.search_with_retry(
            query, streaming, "Hunyuan T1",
            self.temperature, self.max_tokens, self.request_timeout,
            suppress_thinking
        )


class HunyuanT1Latest(BaseSearchModel):
    """Hunyuan T1 Latest 模型 - 使用万码云API，支持搜索功能"""
    
    def __init__(self, api_configs: Dict[str, str]):
        # 使用特殊的API配置
        self.wcode_api_config = {
            "base": "https://wcode.net/api/gpt/v1",
            "key": "sk-1402.tw0EkGK5AeD783OPqyt6DeTtFvVaE9NOE5OXtfDLoR5o28oW"
        }
        super().__init__("hunyuan-t1-latest", api_configs)
    
    def _setup_wcode_api_config(self):
        """设置万码云API配置"""
        openai.api_base = self.wcode_api_config["base"]
        openai.api_key = self.wcode_api_config["key"]
    
    def search(self, query: str, streaming: bool = True, max_retries: int = 2, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """调用 Hunyuan T1 Latest 模型（支持搜索）"""
        # 使用万码云API配置
        self._setup_wcode_api_config()
        
        # 直接使用基类的search_with_retry方法，但重写API调用部分
        return self._search_with_wcode_api_simple(query, streaming, "Hunyuan T1 Latest", suppress_thinking)
    
    def _search_with_wcode_api_simple(self, query: str, streaming: bool = True, model_display_name: str = None, suppress_thinking: bool = True) -> Tuple[Optional[str], Any]:
        """使用万码云API的简化搜索方法"""
        if model_display_name is None:
            model_display_name = self.model_name
            
        try:
            start_time = time.time()
            print(f"调用 {model_display_name} API (万码云)")
            print(f"API Base: {openai.api_base}")
            print(f"Model: {self.model_name}")
            print("🔍 搜索功能已开启")

            # 使用搜索增强参数
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{'role': 'user', 'content': query}],
                stream=streaming,
                temperature=0.7,
                max_tokens=3000,
                request_timeout=150,
                force_search_enhancement=True  # 开启搜索增强
            )
            msg = None

            if streaming:
                msg, completion = self._process_streaming_response(completion, suppress_thinking)
            else:
                if not completion.choices:
                    raise ValueError("No choices returned from API.")
                msg = completion.choices[0].message['content']
                if suppress_thinking and msg:
                    msg = self._extract_final_answer(msg)

            if msg:
                end_time = time.time()
                print(f"耗时: {end_time - start_time:.2f} 秒    {model_display_name} (搜索增强) output: {msg}")
                return msg, completion
            else:
                raise ValueError("No valid response received from API")

        except Exception as err:
            print(f"API Error: {str(err)}")
            print(f"Error type: {type(err).__name__}")
            print(f"❌ {model_display_name} 调用失败")
            return None, None
