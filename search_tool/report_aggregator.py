"""
报告汇总器模块
将多个模型的回答整合成带来源标注的汇总报告
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from parallel_executor import ModelResult
import time


@dataclass
class AggregatedReport:
    """汇总报告"""
    query: str
    timestamp: str
    total_models: int
    successful_models: int
    failed_models: int
    execution_summary: Dict[str, Any]
    model_responses: List[Dict[str, Any]]
    summary_text: str


class ReportAggregator:
    """报告汇总器"""
    
    def __init__(self):
        self.report_templates = {
            "table": self._generate_table_report,
            "list": self._generate_list_report,
            "structured": self._generate_structured_report,
            "comparison": self._generate_comparison_report
        }
    
    def aggregate_results(self, query: str, results: List[ModelResult], 
                         format_type: str = "structured") -> AggregatedReport:
        """
        汇总多个模型的结果
        
        Args:
            query: 原始查询
            results: 模型执行结果列表
            format_type: 报告格式类型
            
        Returns:
            汇总报告
        """
        # 统计信息
        total_models = len(results)
        successful_models = len([r for r in results if r.status == "success"])
        failed_models = len([r for r in results if r.status != "success"])
        
        # 执行摘要
        execution_summary = self._calculate_execution_summary(results)
        
        # 模型响应详情
        model_responses = []
        def _strip_think(text: str) -> str:
            """移除 <think>...</think> 段，防止思维内容出现在报告中"""
            import re
            if not text:
                return text
            # 去除成对标签内容
            text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE)
            # 兜底：去除孤立标签
            text = text.replace("<think>", "").replace("</think>", "")
            return text

        for result in results:
            response_info = {
                "model_key": result.model_key,
                "model_name": result.model_name,
                "status": result.status,
                "execution_time": result.execution_time,
                "response": _strip_think(result.response) if result.status == "success" else result.error_message,
                "response_length": len(_strip_think(result.response)) if result.status == "success" else 0
            }
            model_responses.append(response_info)
        
        # 生成汇总文本
        summary_text = self._generate_summary_text(query, model_responses, execution_summary)
        
        # 创建汇总报告
        report = AggregatedReport(
            query=query,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_models=total_models,
            successful_models=successful_models,
            failed_models=failed_models,
            execution_summary=execution_summary,
            model_responses=model_responses,
            summary_text=summary_text
        )
        
        return report
    
    def generate_report(self, report: AggregatedReport, format_type: str = "structured") -> str:
        """
        生成指定格式的报告
        
        Args:
            report: 汇总报告
            format_type: 报告格式类型
            
        Returns:
            格式化的报告文本
        """
        if format_type in self.report_templates:
            return self.report_templates[format_type](report)
        else:
            return self._generate_structured_report(report)
    
    def _calculate_execution_summary(self, results: List[ModelResult]) -> Dict[str, Any]:
        """计算执行摘要"""
        successful_results = [r for r in results if r.status == "success"]
        
        if not successful_results:
            return {
                "total_time": 0,
                "average_time": 0,
                "min_time": 0,
                "max_time": 0,
                "success_rate": 0
            }
        
        total_time = sum(r.execution_time for r in successful_results)
        avg_time = total_time / len(successful_results)
        min_time = min(r.execution_time for r in successful_results)
        max_time = max(r.execution_time for r in successful_results)
        success_rate = len(successful_results) / len(results)
        
        return {
            "total_time": total_time,
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "success_rate": success_rate
        }
    
    def _generate_summary_text(self, query: str, model_responses: List[Dict], 
                              execution_summary: Dict[str, Any]) -> str:
        """生成汇总文本"""
        successful_responses = [r for r in model_responses if r["status"] == "success"]
        
        if not successful_responses:
            return f"❌ 查询失败：所有模型都无法提供有效回答\n\n查询内容：{query}"
        
        summary = f"📋 查询汇总报告\n"
        summary += f"🔍 查询内容：{query}\n"
        summary += f"📊 执行统计：{len(successful_responses)}/{len(model_responses)} 个模型成功\n"
        summary += f"⏱️  平均耗时：{execution_summary['average_time']:.2f}秒\n\n"
        
        # 按响应长度排序，通常更长的回答包含更多信息
        sorted_responses = sorted(successful_responses, key=lambda x: x["response_length"], reverse=True)
        
        for i, response in enumerate(sorted_responses, 1):
            summary += f"🤖 {i}. {response['model_name']}\n"
            summary += f"   ⏱️  耗时：{response['execution_time']:.2f}秒\n"
            summary += f"   📝 回答：{response['response'][:200]}"
            if len(response['response']) > 200:
                summary += "..."
            summary += "\n\n"
        
        return summary
    
    def _generate_table_report(self, report: AggregatedReport) -> str:
        """生成表格格式报告"""
        output = "=" * 100 + "\n"
        output += f"📋 多模型查询汇总报告 - {report.timestamp}\n"
        output += "=" * 100 + "\n"
        output += f"🔍 查询内容：{report.query}\n"
        output += f"📊 执行统计：{report.successful_models}/{report.total_models} 个模型成功\n"
        output += f"⏱️  平均耗时：{report.execution_summary['average_time']:.2f}秒\n"
        output += "=" * 100 + "\n\n"
        
        # 表格头部
        output += f"{'序号':<4} {'模型名称':<25} {'状态':<8} {'耗时(秒)':<10} {'响应长度':<10}\n"
        output += "-" * 100 + "\n"
        
        # 表格内容
        for i, response in enumerate(report.model_responses, 1):
            status_icon = "✅" if response["status"] == "success" else "❌"
            output += f"{i:<4} {response['model_name']:<25} {status_icon:<8} "
            output += f"{response['execution_time']:<10.2f} {response['response_length']:<10}\n"
        
        output += "-" * 100 + "\n\n"
        
        # 详细回答
        output += "📝 详细回答内容：\n"
        output += "=" * 100 + "\n"
        
        for i, response in enumerate(report.model_responses, 1):
            if response["status"] == "success":
                output += f"\n🤖 {i}. {response['model_name']}\n"
                output += f"⏱️  耗时：{response['execution_time']:.2f}秒\n"
                output += f"📝 回答：\n{response['response']}\n"
                output += "-" * 80 + "\n"
        
        return output
    
    def _generate_list_report(self, report: AggregatedReport) -> str:
        """生成列表格式报告"""
        output = f"📋 多模型查询汇总报告\n"
        output += f"⏰ 生成时间：{report.timestamp}\n"
        output += f"🔍 查询内容：{report.query}\n\n"
        
        output += f"📊 执行统计：\n"
        output += f"  • 总模型数：{report.total_models}\n"
        output += f"  • 成功模型：{report.successful_models}\n"
        output += f"  • 失败模型：{report.failed_models}\n"
        output += f"  • 成功率：{report.execution_summary['success_rate']:.1%}\n"
        output += f"  • 平均耗时：{report.execution_summary['average_time']:.2f}秒\n\n"
        
        output += f"🤖 模型回答：\n"
        for i, response in enumerate(report.model_responses, 1):
            output += f"\n{i}. {response['model_name']}\n"
            if response["status"] == "success":
                output += f"   状态：✅ 成功\n"
                output += f"   耗时：{response['execution_time']:.2f}秒\n"
                output += f"   回答：{response['response']}\n"
            else:
                output += f"   状态：❌ 失败\n"
                output += f"   错误：{response['response']}\n"
        
        return output
    
    def _generate_structured_report(self, report: AggregatedReport) -> str:
        """生成结构化报告"""
        output = "=" * 100 + "\n"
        output += f"🚀 多模型并行查询汇总报告\n"
        output += "=" * 100 + "\n"
        output += f"📅 生成时间：{report.timestamp}\n"
        output += f"🔍 查询内容：{report.query}\n"
        output += "=" * 100 + "\n\n"
        
        # 执行摘要
        output += "📊 执行摘要\n"
        output += "-" * 50 + "\n"
        output += f"🎯 总模型数：{report.total_models}\n"
        output += f"✅ 成功模型：{report.successful_models}\n"
        output += f"❌ 失败模型：{report.failed_models}\n"
        output += f"📈 成功率：{report.execution_summary['success_rate']:.1%}\n"
        output += f"⏱️  平均耗时：{report.execution_summary['average_time']:.2f}秒\n"
        output += f"⚡ 最快响应：{report.execution_summary['min_time']:.2f}秒\n"
        output += f"🐌 最慢响应：{report.execution_summary['max_time']:.2f}秒\n\n"
        
        # 模型回答详情
        output += "🤖 模型回答详情\n"
        output += "=" * 100 + "\n"
        
        successful_responses = [r for r in report.model_responses if r["status"] == "success"]
        if successful_responses:
            # 按响应长度排序
            sorted_responses = sorted(successful_responses, key=lambda x: x["response_length"], reverse=True)
            
            for i, response in enumerate(sorted_responses, 1):
                output += f"\n🎯 {i}. {response['model_name']}\n"
                output += f"   ⏱️  执行时间：{response['execution_time']:.2f}秒\n"
                output += f"   📏 回答长度：{response['response_length']} 字符\n"
                output += f"   📝 回答内容：\n"
                output += f"   {'─' * 60}\n"
                
                # 格式化回答内容
                lines = response['response'].split('\n')
                for line in lines:
                    if line.strip():
                        output += f"   {line}\n"
                    else:
                        output += f"   \n"
                
                output += f"   {'─' * 60}\n"
        else:
            output += "❌ 没有成功的模型回答\n"
        
        # 失败模型信息
        failed_responses = [r for r in report.model_responses if r["status"] != "success"]
        if failed_responses:
            output += f"\n❌ 失败模型信息\n"
            output += "-" * 50 + "\n"
            for response in failed_responses:
                output += f"• {response['model_name']}: {response['response']}\n"
        
        output += "\n" + "=" * 100 + "\n"
        output += "🎉 报告生成完成！\n"
        output += "=" * 100
        
        return output
    
    def _generate_comparison_report(self, report: AggregatedReport) -> str:
        """生成对比格式报告"""
        output = f"📊 多模型回答对比报告\n"
        output += f"⏰ 生成时间：{report.timestamp}\n"
        output += f"🔍 查询内容：{report.query}\n\n"
        
        successful_responses = [r for r in report.model_responses if r["status"] == "success"]
        if not successful_responses:
            return output + "❌ 没有成功的模型回答可供对比"
        
        # 按模型名称排序
        sorted_responses = sorted(successful_responses, key=lambda x: x["model_name"])
        
        output += "🤖 模型回答对比：\n"
        output += "=" * 100 + "\n"
        
        for i, response in enumerate(sorted_responses, 1):
            output += f"\n{i}. {response['model_name']}\n"
            output += f"   执行时间：{response['execution_time']:.2f}秒\n"
            output += f"   回答长度：{response['response_length']} 字符\n"
            output += f"   回答内容：\n"
            output += f"   {'─' * 60}\n"
            output += f"   {response['response']}\n"
            output += f"   {'─' * 60}\n"
        
        return output
    
    def export_report(self, report: AggregatedReport, format_type: str = "structured", 
                     filename: Optional[str] = None) -> str:
        """
        导出报告到文件
        
        Args:
            report: 汇总报告
            format_type: 报告格式
            filename: 文件名（可选）
            
        Returns:
            文件路径
        """
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"multi_model_report_{timestamp}.txt"
        
        report_content = self.generate_report(report, format_type)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return filename
        except Exception as e:
            print(f"❌ 导出报告失败: {str(e)}")
            return ""

