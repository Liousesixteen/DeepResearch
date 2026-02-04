# 统一联网搜索工具 (Search Tool 03)

一个强大的多AI模型联网搜索工具包，提供统一的接口来调用多种AI模型的联网搜索功能，支持智能模型选择、并行执行、结果汇总等高级功能。

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [支持的模型](#支持的模型)
- [安装说明](#安装说明)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [配置说明](#配置说明)
- [架构设计](#架构设计)
- [常见问题](#常见问题)
- [注意事项](#注意事项)

## 🎯 项目简介

Search Tool 03 是一个统一的AI模型联网搜索工具包，它整合了多个主流AI模型的联网搜索能力，为用户提供：

- **统一的接口**：通过一个工具访问多种AI模型的搜索功能
- **智能选择**：根据问题特征自动选择最合适的模型
- **并行执行**：同时调用多个模型，提高效率
- **结果汇总**：自动整合多个模型的回答，生成对比报告
- **高可用性**：支持主备API切换、自动重试、错误处理

## ✨ 功能特性

### 1. 多种使用模式

- **智能模式**：直接输入问题，系统自动选择3-5个最合适的模型
- **手动模式**：手动选择单个或多个模型进行查询
- **并行模式**：同时执行多个模型，快速获得多个回答

### 2. 智能模型选择

- 基于问题类型、语言、复杂度等因素自动选择模型
- 支持按合适度阈值筛选模型
- 失败时自动使用快表替补模型

### 3. 并行执行

- 支持最多5个模型同时执行
- 流式输出，实时显示结果
- 自动抑制thinking过程，只显示最终答案

### 4. 报告汇总

- 自动整合多个模型的回答
- 支持多种报告格式（表格、列表、结构化、对比）
- 可导出报告到文件

### 5. 高可用性

- 主备API自动切换
- 智能错误重试机制
- 网络错误自动重试，权限错误立即降级
- 预构建快表系统，快速替补失败模型

### 6. 流式输出

- 实时显示模型回答
- 支持抑制thinking过程
- 并行模式下同步输出

## 🤖 支持的模型

### 搜索专用模型

1. **Google Deep Research** (`google_deep_research`)
   - 模型ID: `gemini-2.5-flash-deepsearch`
   - 特点: 搜索能力强，信息准确，适合研究类问题

2. **Google Deep Research Pro** (`google_deep_research_pro`)
   - 模型ID: `gemini-2.5-pro-deepsearch`
   - 特点: 处理复杂问题，深度分析，专业领域

3. **Grok Deep Search** (`grok_deep_search`)
   - 模型ID: `grok-3-deepsearch`
   - 特点: 创新思维，逻辑推理，创意生成

4. **DeepSeek Search** (`deepseek_search`)
   - 模型ID: `deepseek-r1-searching`
   - 特点: 技术专业，代码理解，搜索精准

5. **Kimi Search** (`kimi_search`)
   - 模型ID: `kimi-k2-0711-preview-search`
   - 特点: 中文友好，搜索快速，准确度高

6. **GPT Search** (`gpt_search`)
   - 模型ID: `gpt-4o-search-preview-2025-03-11`
   - 特点: 通用性强，搜索平衡，稳定性好

### 通用AI模型

7. **Gemini 2.5 Flash All** (`gemini_25_flash_all`)
   - 模型ID: `gemini-2.5-flash-all`
   - 特点: 响应快速，效率高，多模态

8. **Gemini 2.5 Pro All** (`gemini_25_pro_all`)
   - 模型ID: `gemini-2.5-pro-all`
   - 特点: 专业全面，深度理解，多领域

9. **GPT-4 Gizmo** (`gpt4_gizmo`)
   - 模型ID: `gpt-4-gizmo-*`
   - 特点: 工具使用，功能丰富，实用性强

10. **GPT-4 All** (`gpt4_all`)
    - 模型ID: `gpt-4-all`
    - 特点: 全面通用，稳定可靠，质量高

11. **GPT-4o All** (`gpt4o_all`)
    - 模型ID: `gpt-4o-all`
    - 特点: 最新模型，多模态，先进技术

12. **GPT-4o Mini All** (`gpt4o_mini_all`)
    - 模型ID: `gpt-4o-mini-all`
    - 特点: 性价比之选，快速响应

### 其他模型

13. **Hunyuan T1 Latest** (`hunyuan_t1_latest`)
    - 模型ID: `hunyuan-t1-latest`
    - 特点: 最新中文模型，搜索增强，万码云API

14. **O3 Deep Research** (`o3_deep_research`)
    - 模型ID: `o3-deep-research`
    - 特点: 专业深度，研究能力，高质量

15. **O3 Deep Research 2025-06-26** (`o3_deep_research_20250626`)
    - 模型ID: `o3-deep-research-2025-06-26`
    - 特点: 专业搜索，深度研究，云雾平台

16. **O4 Mini Deep Research** (`o4_mini_deep_research`)
    - 模型ID: `o4-mini-deep-research`
    - 特点: 平衡性能，标准质量，稳定可靠

17. **O4 Mini Deep Research 2025-06-26** (`o4_mini_deep_research_20250626`)
    - 模型ID: `o4-mini-deep-research-2025-06-26`
    - 特点: 快速响应，轻量级，效率高

18. **DeepSeek V3** (`deepseek_v3`)
    - 模型ID: `deepseek-v3-250324`
    - 特点: 最新技术，先进算法，性能优秀

## 📦 安装说明

### 环境要求

- Python 3.7+
openai>=0.27.0
- 网络连接（用于API调用）

### 安装步骤

1. **获取项目文件**

将项目文件夹下载或解压到本地目录。

2. **安装依赖包**

项目需要安装以下Python包：

```bash
# 方法1：使用requirements.txt安装（推荐）
pip install -r requirements.txt

# 方法2：直接安装openai包
pip install openai
```

**依赖说明**：
- **openai**: 用于调用AI模型的API客户端库
  - 安装命令：`pip install openai`
  - 注意：项目使用 `openai` 库作为API客户端，但实际调用的是兼容OpenAI API格式的第三方API服务（如云雾AI、OpenKey等）

**Python标准库**（无需安装）：
- `time` - 时间处理
- `threading` - 多线程支持
- `json` - JSON数据处理
- `os` - 操作系统接口
- `sys` - 系统相关参数和函数
- `re` - 正则表达式
- `abc` - 抽象基类
- `typing` - 类型提示
- `dataclasses` - 数据类
- `enum` - 枚举类型
- `pathlib` - 路径操作
- `concurrent.futures` - 并发执行

3. **配置API密钥**

编辑 `search_tool_03/models_registry.py` 文件，修改API配置：

```python
self._api_configs: Dict[str, str] = {
    "primary_base": "https://yunwu.ai/v1",  # 主API地址
    "primary_key": "your-primary-api-key",  # 主API密钥
    "backup_base": "https://openkey.cloud/v1",  # 备用API地址
    "backup_key": "your-backup-api-key"  # 备用API密钥
}
```

## 🚀 快速开始

### 运行主程序

```bash
cd search_tool_03
python main.py
```

### 基本使用流程

1. **启动程序**：运行 `python main.py`
2. **查看模型列表**：程序会显示所有可用模型
3. **选择使用方式**：
   - **智能模式**：直接输入问题，系统自动选择模型
   - **手动模式**：输入模型编号（如：`1`）
   - **并行模式**：输入多个模型编号，用逗号分隔（如：`1,3,5`）
4. **输入问题**：根据提示输入您的问题
5. **查看结果**：系统会显示模型回答或汇总报告

## 📖 使用指南

### 1. 智能模式（推荐）

智能模式是最便捷的使用方式，系统会根据您的问题自动选择最合适的模型。

**使用方法**：
1. 启动程序后，直接输入您的问题（不要输入数字）
2. 系统会自动分析问题，选择3-5个最合适的模型
3. 并行执行这些模型，生成汇总报告

**示例**：
```
请输入选择 (0-18) 或直接输入您的问题: 什么是人工智能？
```

**特点**：
- 自动分析问题类型、语言、复杂度
- 按合适度排序选择模型
- 失败时自动使用快表替补
- 自动生成汇总报告

### 2. 手动模式

手动选择单个模型进行查询。

**使用方法**：
1. 查看模型列表，记住您想要的模型编号
2. 输入模型编号（如：`1`）
3. 输入您的问题

**示例**：
```
请输入选择 (0-18) 或直接输入您的问题: 1
💬 请输入您的问题:
> 什么是机器学习？
```

### 3. 并行模式

同时使用多个模型进行查询，获得多个回答并对比。

**使用方法**：
1. 输入多个模型编号，用逗号分隔（如：`1,3,5`）
2. 输入您的问题
3. 系统会并行执行这些模型，生成汇总报告

**示例**：
```
请输入选择 (0-18) 或直接输入您的问题: 1,3,5
💬 请输入您的问题:
> 解释一下量子计算的基本原理
```

**特点**：
- 最多支持5个模型并行执行
- 自动生成对比报告
- 可导出报告到文件

### 4. 报告导出

当使用并行模式或智能模式时，系统会询问是否导出报告。

**使用方法**：
- 在报告显示后，输入 `y` 或 `yes` 导出报告
- 报告会保存为文本文件，文件名格式：`multi_model_report_YYYYMMDD_HHMMSS.txt`

### 5. 高级功能

程序还提供了一些高级功能（在帮助菜单中）：

- **查看模型详细信息**：了解每个模型的特点和适用场景
- **查看API配置**：查看当前使用的API配置
- **显示帮助信息**：查看详细的使用说明

## ⚙️ 配置说明

### API配置

API配置在 `models_registry.py` 文件中：

```python
self._api_configs: Dict[str, str] = {
    "primary_base": "https://yunwu.ai/v1",      # 主API基础地址
    "primary_key": "your-api-key",              # 主API密钥
    "backup_base": "https://openkey.cloud/v1", # 备用API基础地址
    "backup_key": "your-backup-key"            # 备用API密钥
}
```

### 模型参数配置

每个模型的参数可以在 `models_impl.py` 中自定义：

```python
class GoogleDeepResearch(BaseSearchModel):
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("gemini-2.5-flash-deepsearch", api_configs)
        self.temperature = 0.7      # 温度参数
        self.max_tokens = 3000     # 最大token数
        self.request_timeout = 150 # 请求超时时间（秒）
```

### 并行执行配置

并行执行器的配置在 `main.py` 中：

```python
self.parallel_executor = ParallelModelExecutor(
    max_workers=5,    # 最大并发数
    timeout=300       # 超时时间（秒）
)
```

### 智能选择配置

智能选择器的阈值配置在 `main.py` 中：

```python
threshold_models = select_models_for_query_by_threshold(
    query, 
    threshold_percent=70.0  # 合适度阈值（百分比）
)
```

## 🏗️ 架构设计

### 模块结构

```
search_tool_03/
├── __init__.py              # 包初始化，导出公共接口
├── main.py                   # 主程序，用户界面
├── models_impl.py            # 模型实现，各种AI模型的封装
├── models_registry.py        # 模型注册表，管理所有模型
├── parallel_executor.py      # 并行执行器，多模型并行调用
├── prebuilt_fast_table.py    # 预构建快表，模型可用性管理
├── report_aggregator.py      # 报告汇总器，结果整合和报告生成
└── smart_model_selector.py   # 智能选择器，自动选择模型
```

### 核心组件

1. **BaseSearchModel**：所有模型的基类，提供统一的搜索接口和错误处理
2. **ModelRegistry**：模型注册表，管理模型注册、获取、配置
3. **ParallelModelExecutor**：并行执行器，使用线程池并行执行多个模型
4. **SmartModelSelector**：智能选择器，基于问题特征选择模型
5. **ReportAggregator**：报告汇总器，整合多个模型的结果
6. **PrebuiltFastTable**：预构建快表，快速获取可用模型列表

### 工作流程

1. **用户输入** → `main.py` 接收用户输入
2. **模型选择** → `smart_model_selector.py` 分析问题并选择模型
3. **并行执行** → `parallel_executor.py` 并行调用多个模型
4. **结果收集** → 收集所有模型的回答
5. **报告生成** → `report_aggregator.py` 生成汇总报告
6. **结果展示** → 显示报告或导出文件

### 错误处理机制

1. **API错误分类**：
   - 可重试错误：网络错误、超时、服务器错误（5xx）
   - 不可重试错误：权限错误、quota不足、无效请求

2. **重试策略**：
   - 主API重试3次
   - 失败后切换到备用API
   - 备用API重试3次
   - 全部失败后返回错误

3. **替补机制**：
   - 使用预构建快表获取可用模型
   - 自动替补失败的模型
   - 确保至少获得3个成功结果

## ❓ 常见问题

### Q1: 如何添加新的模型？

**A**: 在 `models_impl.py` 中创建新的模型类，继承 `BaseSearchModel`，然后在 `models_registry.py` 中注册：

```python
# 1. 在 models_impl.py 中创建模型类
class MyNewModel(BaseSearchModel):
    def __init__(self, api_configs: Dict[str, str]):
        super().__init__("my-model-id", api_configs)
        self.temperature = 0.7
        self.max_tokens = 3000
        self.request_timeout = 150
    
    def search(self, query: str, streaming: bool = True, ...):
        return self.search_with_retry(query, streaming, "My New Model", ...)

# 2. 在 models_registry.py 中注册
default_models = {
    "my_new_model": {
        "class": MyNewModel,
        "name": "My New Model",
        "description": "我的新模型",
        "model_id": "my-model-id"
    }
}
```

### Q2: API调用失败怎么办？

**A**: 系统会自动处理：
1. 主API失败时自动切换到备用API
2. 网络错误会自动重试
3. 权限错误会立即降级，不会浪费时间重试
4. 如果所有API都失败，会显示错误信息

### Q3: 如何修改模型选择逻辑？

**A**: 编辑 `smart_model_selector.py` 文件：
- 修改 `model_features` 字典，添加或修改模型特征
- 调整 `analyze_query` 方法中的评分逻辑
- 修改 `select_models_by_threshold` 方法的阈值

### Q4: 并行执行时输出混乱怎么办？

**A**: 系统已经实现了输出同步机制：
- 使用 `output_lock` 确保并行输出不会混乱
- 每个模型的输出都有标识（`[模型名]`）
- 流式输出会自动同步

### Q5: 如何提高执行速度？

**A**: 可以：
1. 减少并行模型数量（默认最多5个）
2. 降低 `threshold_percent` 阈值，减少选择的模型数
3. 调整 `request_timeout` 超时时间
4. 使用更快的模型（如 Flash 系列）

### Q6: 报告格式有哪些？

**A**: 支持4种格式：
- `structured`：结构化报告（默认，推荐）
- `table`：表格格式
- `list`：列表格式
- `comparison`：对比格式

### Q7: 如何更新快表？

**A**: 快表系统是纯手动模式，需要通过 `build_fast_table.py`（如果存在）手动更新，或者直接编辑 `model_availability_cache.json` 文件。

## ⚠️ 注意事项

1. **API密钥安全**：
   - 不要将API密钥提交到公共仓库
   - 建议使用环境变量或配置文件管理密钥
   - 定期更换API密钥

2. **API配额**：
   - 注意API调用次数限制
   - 并行执行会消耗更多配额
   - 建议合理使用，避免过度调用

3. **网络连接**：
   - 确保网络连接稳定
   - 某些模型可能需要较长时间响应
   - 建议在网络良好的环境下使用

4. **错误处理**：
   - 系统会自动重试和降级
   - 如果所有模型都失败，请检查网络和API配置
   - 查看错误信息了解具体原因

5. **性能优化**：
   - 并行执行会占用更多资源
   - 建议根据机器性能调整 `max_workers`
   - 超时时间根据问题复杂度调整

6. **模型选择**：
   - 智能选择基于问题特征，可能不完全准确
   - 对于特定需求，建议手动选择模型
   - 可以查看模型描述了解适用场景

7. **报告导出**：
   - 报告文件会保存在当前目录
   - 文件名包含时间戳，避免覆盖
   - 报告可能包含大量文本，注意磁盘空间

## 📝 更新日志

### v1.3.1
- 初始版本发布
- 支持17个AI模型
- 实现智能模型选择
- 实现并行执行
- 实现报告汇总
- 实现预构建快表系统

## 📄 许可证

本项目仅供学习和研究使用。

## 📧 联系方式

如有问题或建议，请通过邮件或其他方式反馈。

---



