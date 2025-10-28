"""
研报摘要生成模块
上传5000字以内行业研报，8秒内输出结构化摘要
"""
from typing import List, Dict, Any, Optional
import re
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ReportSummary:
    """结构化研报摘要"""
    title: str
    core_viewpoints: List[str]
    data_support: List[Dict[str, Any]]
    trend_judgment: str
    key_findings: List[str]
    risk_analysis: List[str]
    recommendations: List[str]
    confidence: float


class ReportSummarizer:
    """研报摘要生成器"""
    
    def __init__(self):
        # 核心观点关键词
        self.viewpoint_keywords = [
            '认为', '预期', '看好', '看淡', '预计', '预测',
            '维持', '上调', '下调', '建议', '推荐'
        ]
        
        # 数据关键词
        self.data_keywords = [
            '增长', '下降', '上升', '持平', '%', '增长率',
            '元/吨', '万吨', '亿元', '亿美元', '同比', '环比'
        ]
        
        # 趋势判断关键词
        self.trend_keywords = [
            '趋势', '走势', '方向', '前景', '预期',
            '持续', '波动', '回暖', '下滑', '复苏'
        ]
        
        # 风险关键词
        self.risk_keywords = [
            '风险', '不确定性', '挑战', '压力', '担忧',
            '波动', '影响', '冲击', '抑制'
        ]
        
        # 建议关键词
        self.recommendation_keywords = [
            '建议', '推荐', '关注', '谨慎', '积极',
            '配置', '持有', '买入', '卖出'
        ]
    
    def summarize(self, report_text: str, max_length: int = 5000) -> ReportSummary:
        """
        生成研报摘要
        
        Args:
            report_text: 研报文本（5000字以内）
            max_length: 最大字数限制
        
        Returns:
            ReportSummary: 结构化摘要
        """
        if len(report_text) > max_length:
            report_text = report_text[:max_length] + "..."
        
        try:
            # 提取标题
            title = self._extract_title(report_text)
            
            # 提取核心观点
            core_viewpoints = self._extract_core_viewpoints(report_text)
            
            # 提取数据支撑
            data_support = self._extract_data_support(report_text)
            
            # 提取趋势判断
            trend_judgment = self._extract_trend_judgment(report_text)
            
            # 提取关键发现
            key_findings = self._extract_key_findings(report_text)
            
            # 提取风险分析
            risk_analysis = self._extract_risk_analysis(report_text)
            
            # 提取建议
            recommendations = self._extract_recommendations(report_text)
            
            # 计算置信度
            confidence = self._calculate_confidence(report_text, {
                'core_viewpoints': core_viewpoints,
                'data_support': data_support,
                'trend_judgment': trend_judgment
            })
            
            return ReportSummary(
                title=title,
                core_viewpoints=core_viewpoints,
                data_support=data_support,
                trend_judgment=trend_judgment,
                key_findings=key_findings,
                risk_analysis=risk_analysis,
                recommendations=recommendations,
                confidence=confidence
            )
        
        except Exception as e:
            # 返回基础摘要
            return ReportSummary(
                title="未识别标题",
                core_viewpoints=["文本解析失败"],
                data_support=[],
                trend_judgment="无法判断",
                key_findings=[],
                risk_analysis=[],
                recommendations=[],
                confidence=0.0
            )
    
    def _extract_title(self, text: str) -> str:
        """提取标题"""
        # 尝试从文本开头提取标题
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith(('摘要', '核心', '一、', '二、')):
                return line
        
        return "未识别标题"
    
    def _extract_core_viewpoints(self, text: str) -> List[str]:
        """提取核心观点"""
        viewpoints = []
        
        # 查找包含观点关键词的句子
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            for keyword in self.viewpoint_keywords:
                if keyword in sentence and len(sentence) > 10:
                    # 提取完整观点
                    viewpoint = sentence.strip()
                    if len(viewpoint) > 10 and len(viewpoint) < 200:
                        viewpoints.append(viewpoint)
        
        return list(set(viewpoints))[:5]  # 返回前5个
    
    def _extract_data_support(self, text: str) -> List[Dict[str, Any]]:
        """提取数据支撑"""
        data_items = []
        
        # 查找数据模式
        data_patterns = [
            (r'(\d+(?:\.\d+)?)%', 'percentage'),
            (r'(\d+(?:\.\d+)?)\s*万吨', 'volume'),
            (r'(\d+(?:\.\d+)?)\s*元/吨', 'price'),
            (r'(\d+(?:\.\d+)?)\s*亿元', 'amount'),
            (r'同比增长\s*(\d+(?:\.\d+)?)%', 'growth'),
        ]
        
        for pattern, data_type in data_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                data_items.append({
                    'value': match,
                    'type': data_type,
                    'context': self._get_context(text, match, 50)
                })
        
        return data_items[:10]  # 返回前10个
    
    def _extract_trend_judgment(self, text: str) -> str:
        """提取趋势判断"""
        # 查找包含趋势关键词的句子
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            for keyword in self.trend_keywords:
                if keyword in sentence:
                    # 提取趋势判断
                    trend = sentence.strip()
                    if len(trend) > 20 and len(trend) < 150:
                        return trend
        
        return "趋势分析不明确"
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 查找关键发现标记
        patterns = [
            r'([一二三四五六七八九十\d]+[\.、]?\s*[^。]{20,100})',  # 编号列表
            r'结论[：:]\s*([^。]{20,100})',
            r'发现[：:]\s*([^。]{20,100})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                findings.append(match.strip())
        
        return findings[:5]
    
    def _extract_risk_analysis(self, text: str) -> List[str]:
        """提取风险分析"""
        risk_items = []
        
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            for keyword in self.risk_keywords:
                if keyword in sentence:
                    risk_text = sentence.strip()
                    if len(risk_text) > 15 and len(risk_text) < 150:
                        risk_items.append(risk_text)
        
        return list(set(risk_items))[:5]
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """提取建议"""
        recommendations = []
        
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            for keyword in self.recommendation_keywords:
                if keyword in sentence:
                    rec_text = sentence.strip()
                    if len(rec_text) > 15 and len(rec_text) < 150:
                        recommendations.append(rec_text)
        
        return list(set(recommendations))[:5]
    
    def _get_context(self, text: str, keyword: str, context_length: int = 50) -> str:
        """获取上下文"""
        index = text.find(keyword)
        if index == -1:
            return ""
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(keyword) + context_length)
        
        return text[start:end].strip()
    
    def _calculate_confidence(self, text: str, extracted: Dict) -> float:
        """计算置信度"""
        confidence = 0.0
        
        # 核心观点数量
        if extracted['core_viewpoints']:
            confidence += 0.2
        
        # 数据支撑数量
        if extracted['data_support']:
            confidence += 0.3
        
        # 趋势判断
        if extracted['trend_judgment'] and extracted['trend_judgment'] != "趋势分析不明确":
            confidence += 0.2
        
        # 文本长度
        if len(text) > 500:
            confidence += 0.15
        
        # 结构完整性
        sections = ['摘要', '核心', '数据', '趋势', '风险', '建议']
        found_sections = sum(1 for section in sections if section in text)
        confidence += (found_sections / len(sections)) * 0.15
        
        return min(confidence, 1.0)
    
    def format_summary(self, summary: ReportSummary) -> Dict[str, Any]:
        """格式化摘要为API响应格式"""
        return {
            'title': summary.title,
            'core_viewpoints': summary.core_viewpoints,
            'data_support': summary.data_support,
            'trend_judgment': summary.trend_judgment,
            'key_findings': summary.key_findings,
            'risk_analysis': summary.risk_analysis,
            'recommendations': summary.recommendations,
            'confidence': summary.confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_summary_html(self, summary: ReportSummary) -> str:
        """生成HTML格式的摘要"""
        html = f"""
        <div class="report-summary">
            <h2>{summary.title}</h2>
            
            <section class="core-viewpoints">
                <h3>核心观点</h3>
                <ul>
                    {''.join([f'<li>{vp}</li>' for vp in summary.core_viewpoints])}
                </ul>
            </section>
            
            <section class="data-support">
                <h3>数据支撑</h3>
                <ul>
                    {''.join([f'<li>{item["value"]} {item["type"]}</li>' for item in summary.data_support[:5]])}
                </ul>
            </section>
            
            <section class="trend-judgment">
                <h3>趋势判断</h3>
                <p>{summary.trend_judgment}</p>
            </section>
            
            <section class="key-findings">
                <h3>关键发现</h3>
                <ul>
                    {''.join([f'<li>{finding}</li>' for finding in summary.key_findings])}
                </ul>
            </section>
            
            <section class="risk-analysis">
                <h3>风险分析</h3>
                <ul>
                    {''.join([f'<li>{risk}</li>' for risk in summary.risk_analysis])}
                </ul>
            </section>
            
            <section class="recommendations">
                <h3>投资建议</h3>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in summary.recommendations])}
                </ul>
            </section>
            
            <p class="confidence">置信度: {summary.confidence:.0%}</p>
        </div>
        """
        
        return html

