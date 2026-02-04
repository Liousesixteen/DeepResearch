"""
联网搜索工具主程序
提供统一的用户界面和交互功能
"""

import sys
import os
from typing import Optional, Tuple, Any

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models_registry import get_model_registry, list_models, list_model_info, get_model
from smart_model_selector import (
    get_smart_selector,
    select_model_for_query,
    explain_model_selection,
    select_models_for_query_by_threshold,
)
from parallel_executor import ParallelModelExecutor
from report_aggregator import ReportAggregator


class SearchToolUI:
    """搜索工具用户界面"""
    
    def __init__(self):
        self.registry = get_model_registry()
        self.model_info = list_model_info()
        self.smart_selector = get_smart_selector()
        self.parallel_executor = ParallelModelExecutor(max_workers=5, timeout=300)
        self.report_aggregator = ReportAggregator()
    
    def show_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*80)
        print("🤖 统一联网搜索工具")
        print("="*80)
        print("支持多种AI模型的联网搜索功能")
        print("="*80)
        print("\n👋 你好，请问有什么可以帮助你的吗？")
        print("="*80)
    
    def show_model_menu(self):
        """显示模型选择菜单"""
        print("\n" + "="*80)
        print("📋 可用模型列表")
        print("="*80)
        
        models = list_models()
        for i, model_key in enumerate(models, 1):
            info = self.model_info.get(model_key, {})
            name = info.get("name", model_key.replace("_", " ").title())
            description = info.get("description", "")
            model_id = info.get("model_id", model_key)
            
            print(f"{i:2d}. {name}")
            print(f"    📝 {description}")
            print(f"    🔧 模型ID: {model_id}")
            print()
        
        print("0. 退出程序")
        print("💡 你可以选择模型(可多个)提问；或直接输入问题，系统会自动选择合适的模型进行回答")
        print("-"*80)
        print("🚀 使用说明：")
        print("   • 单个模型：直接输入数字 (如: 1)")
        print("   • 多个模型：输入多个数字，用逗号分隔 (如: 1,3,5)")
        print("   • 智能模式：直接输入问题，系统自动选择模型")
        print("-"*80)
    
    def get_user_choice(self) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[list]]:
        """获取用户选择或问题"""
        models = list_models()
        max_choice = len(models)
        
        while True:
            try:
                choice = input(f"请输入选择 (0-{max_choice}) 或直接输入您的问题: ").strip()
                if not choice:  # 如果用户直接按回车，提示一下
                    print("💡 你可以选择模型(可多个)提问；或直接输入问题，系统会自动选择合适的模型进行回答")
                    continue
                
                # 如果输入是0，退出程序
                if choice == "0":
                    return None, None, None, None
                
                # 检查是否包含逗号（多个模型选择）
                if "," in choice:
                    try:
                        # 解析多个数字选择
                        selected_indices = []
                        for choice_part in choice.split(','):
                            choice_part = choice_part.strip()
                            if choice_part.isdigit():
                                idx = int(choice_part)
                                if 1 <= idx <= max_choice:
                                    selected_indices.append(idx)
                                else:
                                    print(f"❌ 无效选择 {idx}，请输入 1-{max_choice} 之间的数字")
                                    break
                            else:
                                print(f"❌ 无效输入 {choice_part}，请输入数字")
                                break
                        else:
                            if selected_indices:
                                return "MULTI", None, None, selected_indices
                            else:
                                print("❌ 请选择至少一个模型")
                                continue
                    except Exception as e:
                        print(f"❌ 解析多个选择时出错: {str(e)}")
                        continue
                
                # 尝试转换为单个数字
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= max_choice:
                        return choice_num, None, None, None
                    else:
                        print(f"❌ 无效选择，请输入 0-{max_choice} 之间的数字")
                except ValueError:
                    # 不是数字，可能是问题
                    if len(choice) >= 2:  # 问题长度至少2个字符
                        return None, choice, None, None
                    else:
                        print("❌ 请输入有效的数字或至少2个字符的问题")
            except Exception as e:
                print(f"❌ 输入错误: {str(e)}")
    
    def get_query(self) -> str:
        """获取用户查询"""
        print("\n" + "-"*80)
        print("💬 请输入您的问题:")
        print("-"*80)
        
        while True:
            query = input("> ").strip()
            if query:
                return query
            else:
                print("❌ 查询内容不能为空，请重新输入")
    
    def call_selected_model(self, choice: int, query: str) -> bool:
        """调用选定的模型"""
        models = list_models()
        if choice < 1 or choice > len(models):
            print("❌ 无效的模型选择")
            return False
        
        model_key = models[choice - 1]
        info = self.model_info.get(model_key, {})
        model_name = info.get("name", model_key.replace("_", " ").title())
        
        print(f"\n🚀 正在调用 {model_name} 模型...")
        print("-"*80)
        
        try:
            model = get_model(model_key)
            if model is None:
                print(f"❌ 无法获取 {model_name} 模型实例")
                return False
            
            # 调用模型并显示流式输出
            print(f"🚀 开始调用 {model_name} 模型...")
            print("-" * 80)
            
            result = model.search(query, streaming=True, suppress_thinking=True)
            
            if result and result[0] is not None:
                print(f"\n✅ {model_name} 回答完成!")
                return True
            else:
                # 错误信息已经在模型的search_with_retry方法中显示，这里不需要重复
                return False
                
        except Exception as e:
            print(f"\n❌ 调用 {model_name} 时发生错误: {str(e)}")
            return False
    
    def handle_smart_query(self, query: str) -> bool:
        """处理智能查询：按顺序+合适度选择，失败时查快表替补"""
        # 导入快表模块
        try:
            from prebuilt_fast_table import get_global_prebuilt_fast_table
        except ImportError:
            print("❌ 无法导入快表模块，回退到传统模式")
            return self._handle_smart_query_fallback(query)
        
        print("\n" + "="*80)
        print("🚀 智能模式：按顺序+合适度选择，失败时查快表替补")
        print("="*80)
        
        # 1) 首次选择：按原模型顺序+合适度选择（不检测可用性）
        print("🎯 首次选择：按模型顺序+合适度选择模型...")
        
        # 获取按合适度排序的模型列表
        threshold_models = select_models_for_query_by_threshold(query, threshold_percent=70.0)
        if len(threshold_models) < 3:
            top_models = select_model_for_query(query, top_k=8)  # 获取更多候选
            # 合并并去重
            existing_keys = {mk for mk, _, _ in threshold_models}
            for mk, score, info in top_models:
                if mk not in existing_keys:
                    threshold_models.append((mk, score, info))
                    if len(threshold_models) >= 8:
                        break
        
        if not threshold_models:
            print("❌ 无法找到合适的模型")
            return False

        # 智能选择模型数量：不少于3个，最多不超过5个
        # 1. 去重：确保没有重复的模型
        unique_models = []
        seen_keys = set()
        for mk, score, info in threshold_models:
            if mk not in seen_keys:
                unique_models.append((mk, score, info))
                seen_keys.add(mk)
        
        # 2. 动态决定选择数量
        if len(unique_models) <= 3:
            target_count = len(unique_models)  # 如果只有3个或更少，全部选择
        elif len(unique_models) <= 5:
            target_count = len(unique_models)  # 如果3-5个，全部选择
        else:
            # 如果超过5个，选择前5个（按合适度排序）
            target_count = 5
        
        selected_models = unique_models[:target_count]
        
        model_keys = [mk for mk, _, _ in selected_models]
        model_names = [
            self.model_info.get(mk, {}).get("name", mk.replace("_", " ").title())
            for mk in model_keys
        ]

        print(f"✅ 首次选择了 {len(model_keys)} 个模型（按合适度排序，已去重）：")
        for i, (name, (_, score, _)) in enumerate(zip(model_names, selected_models), 1):
            print(f"   {i}. {name} (合适度: {score:.1f}%)")

        # 2) 执行选择的模型
        print(f"\n🚀 开始执行首次选择的模型...")
        print("="*80)
        
        results = self.parallel_executor.execute_models(
            model_keys=model_keys,
            query=query,
            suppress_thinking=True,
            streaming=True,
        )
        
        # 3) 处理结果，如果有失败的模型，使用快表替补
        if results:
            successful_results = [r for r in results if r.status == "success"]
            failed_results = [r for r in results if r.status != "success"]
            
            print(f"\n🎯 首次执行完成！")
            print(f"📊 结果：成功 {len(successful_results)} 个，失败 {len(failed_results)} 个")
            
            # 如果有失败的模型，使用快表替补
            if failed_results and len(successful_results) < 3:
                print(f"\n🔄 检测到失败模型，使用快表替补...")
                replacement_success = self._handle_failed_models_with_fast_table(
                    query, failed_results, successful_results, seen_keys
                )
                # 注意：_handle_failed_models_with_fast_table 已经修改了 successful_results 和 failed_results
                # 不需要重新获取，因为替补结果已经添加到这两个列表中了
            
            # 最终结果处理
            print(f"\n🎯 最终执行完成！")
            print(f"📊 最终结果：成功 {len(successful_results)} 个，失败 {len(failed_results)} 个")
            print("-" * 80)
            
            if successful_results:
                if len(successful_results) >= 2:
                    # 多个成功结果，生成汇总报告
                    print(f"\n📊 正在生成汇总报告...")
                    # 确保报告包含所有成功的模型（包括替补的）
                    report = self.report_aggregator.aggregate_results(query, successful_results)
                    print(f"\n📋 汇总报告：")
                    print("="*80)
                    report_text = self.report_aggregator.generate_report(report, "structured")
                    print(report_text)
                    
                    # 修复：显示正确的总模型数（包含替补成功的）
                    total_successful = len(successful_results)
                    print(f"\n📊 报告统计：")
                    print(f"   • 总模型数：{total_successful}（包含替补成功）")
                    print(f"   • 成功模型：{total_successful}")
                    print(f"   • 失败模型：{len(failed_results)}")
                    print(f"   • 成功率：{(total_successful / (total_successful + len(failed_results)) * 100):.1f}%")

                    # 询问是否导出报告
                    export_choice = input(f"\n💾 是否导出报告到文件？(y/n): ").strip().lower()
                    if export_choice in ['y', 'yes', '是']:
                        filename = self.report_aggregator.export_report(report, "structured")
                        if filename:
                            print(f"✅ 报告已导出到: {filename}")
                        else:
                            print("❌ 导出失败")
                else:
                    # 只有一个成功结果，显示单个回答
                    result = successful_results[0]
                    print(f"\n📝 {result.model_name} 的回答：")
                    print("-" * 80)
                    print(result.response)
                    print("-" * 80)
                
                # 显示失败模型信息
                if failed_results:
                    print(f"\n⚠️  失败的模型：")
                    for result in failed_results:
                        print(f"   • {result.model_name}: {result.status}")
                
                return True
            else:
                print("❌ 没有获得有效的模型回答")
                return False
        else:
            print("❌ 所有模型都调用失败")
            return False
    
    def _handle_smart_query_fallback(self, query: str) -> bool:
        """智能查询的回退方法（传统模式）"""
        print("🔄 使用传统智能模式（基于合适度选择）...")
        
        # 获取按合适度排序的模型列表
        threshold_models = select_models_for_query_by_threshold(query, threshold_percent=70.0)
        if len(threshold_models) < 3:
            top_models = select_model_for_query(query, top_k=10)  # 获取更多候选
            # 合并并去重
            existing_keys = {mk for mk, _, _ in threshold_models}
            for mk, score, info in top_models:
                if mk not in existing_keys:
                    threshold_models.append((mk, score, info))
                    if len(threshold_models) >= 10:
                        break
        
        if not threshold_models:
            print("❌ 无法找到合适的模型")
            return False

        # 智能选择模型数量：不少于3个，最多不超过5个
        # 1. 去重：确保没有重复的模型
        unique_models = []
        seen_keys = set()
        for mk, score, info in threshold_models:
            if mk not in seen_keys:
                unique_models.append((mk, score, info))
                seen_keys.add(mk)
        
        # 2. 动态决定选择数量
        if len(unique_models) <= 3:
            target_count = len(unique_models)  # 如果只有3个或更少，全部选择
        elif len(unique_models) <= 5:
            target_count = len(unique_models)  # 如果3-5个，全部选择
        else:
            # 如果超过5个，选择前5个（按合适度排序）
            target_count = 5
        
        selected_models = unique_models[:target_count]
        
        model_keys = [mk for mk, _, _ in selected_models]
        model_names = [
            self.model_info.get(mk, {}).get("name", mk.replace("_", " ").title())
            for mk in model_keys
        ]

        print(f"✅ 传统模式选择了 {len(model_keys)} 个模型（按合适度排序，已去重）：")
        for i, (name, (_, score, _)) in enumerate(zip(model_names, selected_models), 1):
            print(f"   {i}. {name} (合适度: {score:.1f}%)")

        # 执行选择的模型
        print(f"\n🚀 开始执行传统模式选择的模型...")
        print("="*80)
        
        results = self.parallel_executor.execute_models(
            model_keys=model_keys,
            query=query,
            suppress_thinking=True,
            streaming=True,
        )
        
        # 处理结果
        if results:
            successful_results = [r for r in results if r.status == "success"]
            failed_results = [r for r in results if r.status != "success"]
            
            print(f"\n🎯 执行完成！")
            print(f"📊 最终结果：成功 {len(successful_results)} 个，失败 {len(failed_results)} 个")
            print("-" * 80)
            
            if successful_results:
                if len(successful_results) >= 2:
                    # 多个成功结果，生成汇总报告
                    print(f"\n📊 正在生成汇总报告...")
                    report = self.report_aggregator.aggregate_results(query, successful_results)
                    print(f"\n📋 汇总报告：")
                    print("="*80)
                    report_text = self.report_aggregator.generate_report(report, "structured")
                    print(report_text)

                    # 询问是否导出报告
                    export_choice = input(f"\n💾 是否导出报告到文件？(y/n): ").strip().lower()
                    if export_choice in ['y', 'yes', '是']:
                        filename = self.report_aggregator.export_report(report, "structured")
                        if filename:
                            print(f"✅ 报告已导出到: {filename}")
                        else:
                            print("❌ 导出失败")
                else:
                    # 只有一个成功结果，显示单个回答
                    result = successful_results[0]
                    print(f"\n📝 {result.model_name} 的回答：")
                    print("-" * 80)
                    print(result.response)
                    print("-" * 80)
                
                # 显示失败模型信息
                if failed_results:
                    print(f"\n⚠️  失败的模型：")
                    for result in failed_results:
                        print(f"   • {result.model_name}: {result.status}")
                
                return True
            else:
                print("❌ 没有获得有效的模型回答")
                return False
        else:
            print("❌ 所有模型都调用失败")
            return False
    
    def show_model_info(self):
        """显示模型详细信息"""
        print("\n" + "="*80)
        print("📊 模型详细信息")
        print("="*80)
    
    def handle_multiple_models(self, selected_indices: list) -> bool:
        """处理多个模型选择"""
        print("\n" + "="*80)
        print("🚀 并行执行多个模型")
        print("="*80)
        
        # 显示可用模型
        models = list_models()
        
        # 获取选中的模型键（注意：selected_indices是从1开始的，需要转换为从0开始）
        selected_model_keys = [models[i-1] for i in selected_indices]
        selected_model_names = [self.model_info.get(key, {}).get("name", key.replace("_", " ").title()) 
                              for key in selected_model_keys]
        
        print(f"✅ 已选择 {len(selected_model_keys)} 个模型：")
        for name in selected_model_names:
            print(f"   • {name}")
        
        # 获取查询
        query = self.get_query()
        
        # 执行并行查询
        print(f"\n🚀 开始并行执行 {len(selected_model_keys)} 个模型...")
        results = self.parallel_executor.execute_models(
            model_keys=selected_model_keys,
            query=query,
            suppress_thinking=True,
            streaming=True
        )
        
        # 生成汇总报告
        if results:
            print(f"\n📊 正在生成汇总报告...")
            report = self.report_aggregator.aggregate_results(query, results)
            
            # 显示报告
            print(f"\n📋 汇总报告：")
            print("="*80)
            report_text = self.report_aggregator.generate_report(report, "structured")
            print(report_text)
            
            # 修复：显示正确的统计信息
            successful_results = [r for r in results if r.status == "success"]
            failed_results = [r for r in results if r.status != "success"]
            total_models = len(results)
            total_successful = len(successful_results)
            total_failed = len(failed_results)
            success_rate = (total_successful / total_models * 100) if total_models > 0 else 0
            
            print(f"\n📊 报告统计：")
            print(f"   • 总模型数：{total_models}")
            print(f"   • 成功模型：{total_successful}")
            print(f"   • 失败模型：{total_failed}")
            print(f"   • 成功率：{success_rate:.1f}%")
            
            # 询问是否导出报告
            export_choice = input(f"\n💾 是否导出报告到文件？(y/n): ").strip().lower()
            if export_choice in ['y', 'yes', '是']:
                filename = self.report_aggregator.export_report(report, "structured")
                if filename:
                    print(f"✅ 报告已导出到: {filename}")
                else:
                    print("❌ 导出失败")
            
            return True
        else:
            print("❌ 并行执行失败，没有获得结果")
            return False

    def handle_parallel_execution(self) -> bool:
        """处理并行执行多个模型（保留原有方法以兼容）"""
        print("\n" + "="*80)
        print("🚀 并行执行多个模型")
        print("="*80)
        
        # 显示可用模型
        models = list_models()
        print("📋 可用模型列表：")
        for i, model_key in enumerate(models, 1):
            info = self.model_info.get(model_key, {})
            name = info.get("name", model_key.replace("_", " ").title())
            print(f"{i:2d}. {name}")
        
        # 获取用户选择的模型
        print(f"\n请选择要并行执行的模型（输入数字，用逗号分隔，如：1,3,5）：")
        while True:
            try:
                choice_input = input("> ").strip()
                if not choice_input:
                    print("❌ 请选择至少一个模型")
                    continue
                
                # 解析用户选择
                selected_indices = []
                for choice in choice_input.split(','):
                    choice = choice.strip()
                    if choice.isdigit():
                        idx = int(choice)
                        if 1 <= idx <= len(models):
                            selected_indices.append(idx)
                        else:
                            print(f"❌ 无效选择 {idx}，请输入 1-{len(models)} 之间的数字")
                            break
                    else:
                        print(f"❌ 无效输入 {choice}，请输入数字")
                        break
                else:
                    if selected_indices:
                        break
                    else:
                        print("❌ 请选择至少一个模型")
                        continue
                        
            except Exception as e:
                print(f"❌ 输入错误: {str(e)}")
        
        # 获取选中的模型键
        selected_model_keys = [models[i-1] for i in selected_indices]
        selected_model_names = [self.model_info.get(key, {}).get("name", key.replace("_", " ").title()) 
                              for key in selected_model_keys]
        
        print(f"\n✅ 已选择 {len(selected_model_keys)} 个模型：")
        for name in selected_model_names:
            print(f"   • {name}")
        
        # 获取查询
        query = self.get_query()
        
        # 执行并行查询
        print(f"\n🚀 开始并行执行 {len(selected_model_keys)} 个模型...")
        results = self.parallel_executor.execute_models(
            model_keys=selected_model_keys,
            query=query,
            suppress_thinking=True,
            streaming=True
        )
        
        # 生成汇总报告
        if results:
            print(f"\n📊 正在生成汇总报告...")
            report = self.report_aggregator.aggregate_results(query, results)
            
            # 显示报告
            print(f"\n📋 汇总报告：")
            print("="*80)
            report_text = self.report_aggregator.generate_report(report, "structured")
            print(report_text)
            
            # 修复：显示正确的统计信息
            successful_results = [r for r in results if r.status == "success"]
            failed_results = [r for r in results if r.status != "success"]
            total_models = len(results)
            total_successful = len(successful_results)
            total_failed = len(failed_results)
            success_rate = (total_successful / total_models * 100) if total_models > 0 else 0
            
            print(f"\n📊 报告统计：")
            print(f"   • 总模型数：{total_models}")
            print(f"   • 成功模型：{total_successful}")
            print(f"   • 失败模型：{total_failed}")
            print(f"   • 成功率：{success_rate:.1f}%")
            
            # 询问是否导出报告
            export_choice = input(f"\n💾 是否导出报告到文件？(y/n): ").strip().lower()
            if export_choice in ['y', 'yes', '是']:
                filename = self.report_aggregator.export_report(report, "structured")
                if filename:
                    print(f"✅ 报告已导出到: {filename}")
                else:
                    print("❌ 导出失败")
            
            return True
        else:
            print("❌ 并行执行失败，没有获得结果")
            return False
    
    # def handle_batch_model_selection(self) -> bool:  # 暂时注释掉
    #     """处理批量模型选择"""
    #     print("\n" + "="*80)
    #     print("📋 批量模型选择")
    #     print("="*80)
    #     
    #     # 显示模型分类
    #     print("请选择模型类别：")
    #     print("1. 搜索专用模型（Google Deep Research, Grok等）")
    #     print("2. 通用AI模型（GPT, Gemini等）")
    #     print("3. 中文模型（Hunyuan, DeepSeek等）")
    #     print("4. 自定义选择")
    #     
    #     while True:
    #         try:
    #             category_choice = input("请选择类别 (1-4): ").strip()
    #             if category_choice in ['1', '2', '3', '4']:
    #                 break
    #             else:
    #             print("❌ 请输入 1-4 之间的数字")
    #         except Exception as e:
    #             print(f"❌ 输入错误: {str(e)}")
    #     
    #     # 根据类别选择模型
    #     models = list_models()
    #     if category_choice == '1':
    #         # 搜索专用模型
    #         search_models = ['google_deep_research', 'google_deep_research_pro', 'grok_deep_search', 'deepseek_search', 'kimi_search']
    #         selected_model_keys = [key for key in search_models if key in models]
    #     elif category_choice == '2':
    #         # 通用AI模型
    #         general_models = ['gpt_search', 'gemini_25_flash_all', 'gemini_25_pro_all', 'gpt4_gizmo', 'gpt4_all', 'gpt4o_all']
    #         selected_choice == '3':
    #         # 中文模型
    #         chinese_models = ['hunyuan_t1', 'hunyuan_t1_latest', 'deepseek_v3']
    #         selected_model_keys = [key for key in chinese_models if key in models]
    #     else:
    #         # 自定义选择
    #         return self.handle_parallel_execution()
    #     
    #     if not selected_model_keys:
    #         print("❌ 该类别下没有可用的模型")
    #         return False
    #     
    #     print(f"\n✅ 已选择 {len(selected_model_keys)} 个模型：")
    #     for key in selected_model_keys:
    #         name = self.model_info.get(key, {}).get("name", key.replace("_", " ").title())
    #         print(f"   • {name}")
    #     
    #     # 获取查询
    #     query = self.get_query()
    #     
    #     # 执行并行查询
    #     print(f"\n🚀 开始并行执行 {len(selected_model_keys)} 个模型...")
    #     results = self.parallel_executor.execute_models(
    #         model_keys=selected_model_keys,
    #         query=query,
    #         suppress_thinking=True,
    #         streaming=False
    #     )
    #     
    #     # 生成汇总报告
    #     if results:
    #         print(f"\n📊 正在生成汇总报告...")
    #         report = self.report_aggregator.aggregate_results(query, results)
    #             
    #         # 显示报告
    #         print(f"\n📋 汇总报告：")
    #         print("="*80)
    #         report_text = self.report_aggregator.generate_report(report, "structured")
    #         print(report_text)
    #             
    #         # 询问是否导出报告
    #         export_choice = input(f"\n💾 是否导出报告到文件？(y/n): ").strip().lower()
    #         if export_choice in ['y', 'yes', '是']:
    #             filename = self.report_aggregator.export_report(report, "structured")
    #             if filename:
    #                 print(f"✅ 报告已导出到: {filename}")
    #             else:
    #                 print("   📈 总计: {len(models)} 个模型")
    #         print("-"*80)
    
    def show_api_config(self):
        """显示API配置信息"""
        configs = self.registry.get_api_configs()
        print("\n" + "="*80)
        print("⚙️  API配置信息")
        print("="*80)
        print(f"主API Base: {configs.get('primary_base', 'N/A')}")
        print(f"主API Key: {configs.get('primary_key', 'N/A')[:20]}...")
        print(f"备用API Base: {configs.get('backup_base', 'N/A')}")
        print(f"备用API Key: {configs.get('backup_key', 'N/A')[:20]}...")
        print("-"*80)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n" + "="*80)
        print("❓ 帮助信息")
        print("="*80)
        print("🎯 智能模式:")
        print("   - 直接输入问题，系统会自动选择至少3个合适的模型")
        print("   - 系统会分析问题类型、语言、复杂度等因素")
        print("   - 自动选择最合适的模型，失败时自动替换")
        print("   - 支持多模型汇总报告生成")
        print("\n🔧 手动模式:")
        print("   - 输入对应的数字选择要使用的模型")
        print("   - 然后输入您想要搜索的问题")
        print("   - 系统会调用选定的模型进行联网搜索")
        print("\n🚀 并行执行模式:")
        print("   - 直接输入多个数字，用逗号分隔 (如: 1,3,5)")
        print("   - 支持同时调用多个模型，提高效率")
        print("   - 自动生成汇总报告，对比不同模型的回答")
        print("   - 可选择导出报告到文件")
        print("\n💡 提示:")
        print("   - 所有模型都支持联网搜索功能")
        print("   - 系统会自动处理API负载和重试")
        print("   - 支持流式输出，实时显示回答内容")
        print("   - 如果主API不可用，会自动切换到备用API")
        print("   - 智能模式推荐准确率基于问题特征分析")
        print("   - 并行执行时thinking过程会被抑制，只显示最终结果")
        print("-"*80)
    
    def show_advanced_menu(self):
        """显示高级菜单"""
        print("\n" + "="*80)
        print("🔧 高级功能")
        print("="*80)
        print("1. 查看模型详细信息")
        print("2. 查看API配置")
        print("3. 显示帮助信息")
        print("4. 返回主菜单")
        print("0. 退出程序")
        print("-"*80)
    
    def handle_advanced_menu(self):
        """处理高级菜单"""
        while True:
            self.show_advanced_menu()
            choice = input("请选择功能 (0-4): ").strip()
            
            if choice == "0":
                return False
            elif choice == "1":
                self.show_model_info()
            elif choice == "2":
                self.show_api_config()
            elif choice == "3":
                self.show_help()
            elif choice == "4":
                return True
            else:
                print("❌ 无效选择，请输入 0-4 之间的数字")
    
    def run(self):
        """运行主程序"""
        self.show_welcome()
        
        while True:
            self.show_model_menu()
            choice, smart_query, _, multi_choices = self.get_user_choice()
            
            if choice is None and smart_query is None:
                print("\n👋 感谢使用统一联网搜索工具，再见！")
                break
            
            # 处理多个模型选择
            if choice == "MULTI" and multi_choices:
                success = self.handle_multiple_models(multi_choices)
            elif smart_query:
                # 处理智能查询
                success = self.handle_smart_query(smart_query)
            else:
                # 手动选择单个模型
                query = self.get_query()
                success = self.call_selected_model(choice, query)
            
            # 询问是否继续
            print("\n" + "-"*80)
            continue_choice = input("是否继续使用其他模型？(y/n/h=帮助): ").strip().lower()
            
            if continue_choice in ['h', 'help', '帮助']:
                self.show_help()
            elif continue_choice not in ['y', 'yes', '是']:
                print("\n👋 感谢使用统一联网搜索工具，再见！")
                break

    def _handle_failed_models_with_fast_table(self, query: str, failed_results: list, successful_results: list, seen_keys: set) -> bool:
        """使用预构建快表替补失败的模型（无需等待检测）"""
        print("🔄 使用预构建快表替补失败的模型...")
        
        try:
            # 使用预构建快表系统（无需等待检测）
            from prebuilt_fast_table import get_global_prebuilt_fast_table
            
            prebuilt_table = get_global_prebuilt_fast_table()
            
            # 获取可用的替补模型（直接从缓存返回，无需检测）
            need_count = max(3 - len(successful_results), 1)  # 至少需要1个替补
            available_models = prebuilt_table.get_available_models(
                exclude_keys=seen_keys, 
                min_count=need_count
            )
            
            if not available_models:
                print("⚠️  预构建快表中没有可用的替补模型")
                return False
            
            # 选择替补模型
            max_replacement = min(len(available_models), 5 - len(successful_results))
            replacement_models = available_models[:max_replacement]
            replacement_keys = [mk for mk, _ in replacement_models]
            
            # 获取模型名称
            replacement_names = []
            for mk, stability_score in replacement_models:
                model_info = self.model_info.get(mk, {})
                model_name = model_info.get("name", mk.replace("_", " ").title())
                replacement_names.append((mk, model_name, stability_score))
            
            print(f"✅ 预构建快表选择了 {len(replacement_models)} 个替补模型：")
            for i, (mk, name, stability_score) in enumerate(replacement_names, 1):
                print(f"   {i}. {name} (稳定性评分: {stability_score:.2f})")
            
            # 执行替补模型
            print(f"\n🚀 开始执行替补模型...")
            print("="*80)
            
            replacement_results = self.parallel_executor.execute_models(
                model_keys=replacement_keys,
                query=query,
                suppress_thinking=True,
                streaming=True,
            )
            
            if replacement_results:
                # 将替补结果添加到总结果中
                successful_results.extend([r for r in replacement_results if r.status == "success"])
                failed_results.extend([r for r in replacement_results if r.status != "success"])
                
                print(f"✅ 替补模型执行完成！")
                print(f"📊 替补结果：成功 {len([r for r in replacement_results if r.status == 'success'])} 个")
                return True
            else:
                print("❌ 替补模型执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 预构建快表替补过程异常: {str(e)}")
            return False


def main():
    """主函数"""
    try:
        ui = SearchToolUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {str(e)}")
        print("请检查网络连接和API配置")


if __name__ == "__main__":
    main()
