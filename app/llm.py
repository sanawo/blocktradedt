from __future__ import annotations
from typing import List, Dict, Any

class LLM:
    """本地LLM类，提供简单的摘要功能"""
    
    def __init__(self):
        pass
    
    def generate_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """生成搜索结果摘要"""
        if not results:
            return f"未找到与'{query}'相关的记录。"
        
        parts = []
        for r in results[:5]:  # 只取前5个结果
            l = r["listing"]
            title = l.get("title", "")
            region = l.get("region", "")
            price = l.get("price")
            unit = l.get("unit", "")
            
            if price is not None:
                parts.append(f"{title}（{region}，{price}{unit}）")
            else:
                parts.append(f"{title}（{region}）")
        
        if not parts:
            return f"未找到与'{query}'相关的记录。"
        
        summary = "；".join(parts)
        return f"为您找到以下相关记录：{summary}。这些数据来源于大宗交易市场，仅供参考。"



