"""
整合所有高级功能
包含：复杂查询、研报摘要、知识图谱可视化
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import os
from datetime import datetime

# 导入新功能模块
from app.complex_query_parser import ComplexQueryParser, ComplexQueryExecutor
from app.report_summarizer import ReportSummarizer
from app.kg_visualizer import KnowledgeGraphVisualizer, KGVisualizationHTML

# 全局变量（需要在主应用中初始化）
complex_executor = None
report_summarizer = None
kg_visualizer = None


def init_advanced_features(retriever, kg_builder):
    """初始化高级功能"""
    global complex_executor, report_summarizer, kg_visualizer
    
    complex_executor = ComplexQueryExecutor(retriever, kg_builder)
    report_summarizer = ReportSummarizer()
    kg_visualizer = KnowledgeGraphVisualizer(kg_builder)


def add_advanced_routes(app: FastAPI):
    """添加高级功能路由"""
    
    @app.post("/api/complex/query")
    async def execute_complex_query(query: str, top_k: int = 10):
        """
        执行复杂查询
        
        示例："2025年Kruger收购对漂白针叶木浆价格的影响"
        """
        if not complex_executor:
            raise HTTPException(status_code=503, detail="复杂查询功能未初始化")
        
        try:
            result = complex_executor.execute(query, top_k)
            return {
                "success": True,
                "query": query,
                "parsed": result['parsed'],
                "kg_results": result['kg_results'],
                "text_results": result['text_results'],
                "kg_paths": result['kg_paths'],
                "answer": result['answer'],
                "timestamp": result['timestamp']
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"执行复杂查询失败: {str(e)}")
    
    @app.post("/api/report/summarize")
    async def summarize_report(
        report_text: Optional[str] = None,
        file: Optional[UploadFile] = File(None)
    ):
        """
        生成研报摘要
        
        支持：文本上传或文件上传（5000字以内，8秒内完成）
        """
        if not report_summarizer:
            raise HTTPException(status_code=503, detail="研报摘要功能未初始化")
        
        try:
            # 处理文件上传
            if file:
                content = await file.read()
                report_text = content.decode('utf-8')
            
            if not report_text:
                raise HTTPException(status_code=400, detail="未提供研报文本")
            
            # 生成摘要
            start_time = datetime.now()
            summary = report_summarizer.summarize(report_text)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            # 格式化输出
            formatted = report_summarizer.format_summary(summary)
            
            return {
                "success": True,
                "processing_time": f"{processing_time:.2f}秒",
                "summary": formatted,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成摘要失败: {str(e)}")
    
    @app.post("/api/report/summarize/html")
    async def summarize_report_html(
        report_text: Optional[str] = None,
        file: Optional[UploadFile] = File(None)
    ):
        """生成HTML格式的研报摘要"""
        if not report_summarizer:
            raise HTTPException(status_code=503, detail="研报摘要功能未初始化")
        
        try:
            if file:
                content = await file.read()
                report_text = content.decode('utf-8')
            
            if not report_text:
                raise HTTPException(status_code=400, detail="未提供研报文本")
            
            summary = report_summarizer.summarize(report_text)
            html = report_summarizer.generate_summary_html(summary)
            
            return HTMLResponse(content=html)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成HTML摘要失败: {str(e)}")
    
    @app.post("/api/kg/visualize")
    async def visualize_knowledge_graph(entities: list):
        """
        可视化知识图谱
        
        参数：实体名称列表
        返回：包含节点和边的可视化数据
        """
        if not kg_visualizer:
            raise HTTPException(status_code=503, detail="知识图谱可视化功能未初始化")
        
        try:
            vis_data = kg_visualizer.visualize_query_results(entities, max_depth=2)
            
            return {
                "success": True,
                "data": vis_data,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"可视化失败: {str(e)}")
    
    @app.get("/api/kg/entity/{entity_id}/detail")
    async def get_entity_detail(entity_id: str):
        """获取实体详细信息（用于点击节点查看）"""
        if not kg_visualizer:
            raise HTTPException(status_code=503, detail="知识图谱可视化功能未初始化")
        
        try:
            detail = kg_visualizer.get_entity_detail(entity_id)
            
            return {
                "success": True,
                "entity": detail,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取实体详情失败: {str(e)}")
    
    @app.post("/api/kg/path")
    async def find_path(from_entity: str, to_entity: str):
        """查找两个实体之间的最短路径"""
        if not kg_visualizer:
            raise HTTPException(status_code=503, detail="知识图谱可视化功能未初始化")
        
        try:
            path_result = kg_visualizer.find_shortest_path(from_entity, to_entity)
            
            return {
                "success": True,
                "path": path_result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查找路径失败: {str(e)}")
    
    @app.post("/api/kg/export")
    async def export_knowledge_graph(entities: list, format: str = "cytoscape"):
        """导出知识图谱数据"""
        if not kg_visualizer:
            raise HTTPException(status_code=503, detail="知识图谱可视化功能未初始化")
        
        try:
            if format == "cytoscape":
                data = kg_visualizer.generate_cytoscape_data(entities, max_depth=2)
            else:
                data = kg_visualizer.visualize_query_results(entities, max_depth=2)
            
            json_data = kg_visualizer.export_network_json(entities, max_depth=2, format=format)
            
            return JSONResponse(
                content=json.loads(json_data),
                headers={"Content-Disposition": f'attachment; filename="kg_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'}
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
    
    return app

