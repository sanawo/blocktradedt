"""
增强检索系统演示脚本
展示知识图谱构建、BART微调和智能检索功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.kg_builder import KnowledgeGraphBuilder
from app.pattern_prompter import StructuredPatternPrompter
from app.data_augmentation import DataAugmentation
from app.bart_finetuner import BARTFinetuner
from app.enhanced_retriever import EnhancedRetriever
from app.intent_classifier import IntentClassifier, QueryOptimizer


def demo_knowledge_graph():
    """演示知识图谱构建"""
    print("\n" + "="*60)
    print("1. 知识图谱构建演示")
    print("="*60)
    
    # 创建知识图谱构建器
    kg_builder = KnowledgeGraphBuilder()
    
    # 加载种子数据
    print("\n加载纸浆领域种子数据...")
    kg_builder.load_pulp_domain_seed_data()
    
    # 显示统计信息
    stats = kg_builder.get_statistics()
    print(f"\n知识图谱统计信息:")
    print(f"  - 实体总数: {stats['total_entities']}")
    print(f"  - 关系总数: {stats['total_relations']}")
    print(f"  - 实体类型: {stats['entity_types']}")
    print(f"  - 关系类型: {stats['relation_types']}")
    
    # 保存知识图谱
    output_path = kg_builder.save_to_json("pulp_kg.json")
    print(f"\n知识图谱已保存到: {output_path}")
    
    return kg_builder


def demo_pattern_prompter():
    """演示结构化模式提示器"""
    print("\n" + "="*60)
    print("2. 结构化模式提示器演示")
    print("="*60)
    
    prompter = StructuredPatternPrompter()
    
    # 列出所有模式
    print("\n可用模式:")
    for pattern_name in prompter.list_patterns():
        info = prompter.get_pattern_info(pattern_name)
        print(f"  - {pattern_name}: {info['description']}")
    
    # 生成示例提示
    text = "针叶木浆是一种高质量的纸浆产品，由松木制成，具有高强度、高白度的特点。"
    print(f"\n示例文本: {text}")
    
    prompt = prompter.generate_prompt("pulp_domain", text)
    print(f"\n生成的提示:\n{prompt[:200]}...")
    
    return prompter


def demo_data_augmentation():
    """演示数据增强"""
    print("\n" + "="*60)
    print("3. 数据增强演示")
    print("="*60)
    
    augmenter = DataAugmentation()
    
    original_text = "针叶木浆具有高白度和高强度特性"
    print(f"\n原始文本: {original_text}")
    
    # 同义词替换
    augmented_syn = augmenter.synonym_replacement(original_text)
    print(f"\n同义词替换: {augmented_syn}")
    
    # 改写
    augmented_para = augmenter.paraphrase(original_text)
    print(f"改写版本: {augmented_para}")
    
    # 批量增强
    augmented_texts = augmenter.augment(original_text)
    print(f"\n生成 {len(augmented_texts)} 个增强版本")
    
    return augmenter


def demo_bart_finetuner():
    """演示BART微调"""
    print("\n" + "="*60)
    print("4. BART模型微调演示")
    print("="*60)
    
    finetuner = BARTFinetuner()
    
    # 准备训练数据
    sample_texts = [
        "针叶木浆是一种高质量纸浆",
        "纸浆白度是重要指标",
        "蒸煮是纸浆生产的关键工艺"
    ]
    
    print(f"\n准备训练数据（{len(sample_texts)} 条）...")
    training_data = finetuner.prepare_training_data(sample_texts)
    print(f"生成了 {len(training_data)} 个训练样本")
    
    # 展示训练配置
    print("\n显示训练配置...")
    config = finetuner.train(training_data)
    print(f"训练配置: {config}")
    
    # 测试生成
    test_query = "针叶木浆的特点是什么？"
    generated = finetuner.generate(test_query)
    print(f"\n测试查询: {test_query}")
    print(f"生成结果: {generated}")
    
    return finetuner


def demo_enhanced_retriever():
    """演示增强检索器"""
    print("\n" + "="*60)
    print("5. 增强检索器演示")
    print("="*60)
    
    retriever = EnhancedRetriever()
    
    # 测试查询
    queries = [
        "针叶木浆的生产工艺",
        "纸浆白度指标",
        "晨鸣纸业生产什么纸浆"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        
        # 执行检索
        results = retriever.search(query, top_k=3)
        print(f"找到 {len(results)} 个结果:")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('entity_name', 'N/A')} "
                  f"({result.get('entity_type', 'N/A')}) "
                  f"[得分: {result.get('final_score', 0):.2f}]")
    
    # 获取统计信息
    stats = retriever.get_kg_statistics()
    print(f"\n知识图谱统计: {stats}")
    
    return retriever


def demo_intent_classifier():
    """演示意图分类器"""
    print("\n" + "="*60)
    print("6. 查询意图识别演示")
    print("="*60)
    
    classifier = IntentClassifier()
    optimizer = QueryOptimizer(classifier)
    
    test_queries = [
        "什么是针叶木浆？",
        "针叶木浆的白度是多少？",
        "针叶木浆和阔叶木浆的区别",
        "纸浆价格趋势"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 分类意图
        parsed = classifier.parse_query(query)
        print(f"  意图: {parsed['intent']} (置信度: {parsed['confidence']:.2f})")
        print(f"  实体: {parsed['entities']}")
        print(f"  属性: {parsed['attributes']}")
        
        # 优化查询
        optimized = optimizer.optimize(query)
        if optimized['optimized_query'] != query:
            print(f"  优化后: {optimized['optimized_query']}")
    
    return classifier, optimizer


def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n" + "="*60)
    print("7. 完整工作流程演示")
    print("="*60)
    
    # 构建知识图谱
    kg_builder = KnowledgeGraphBuilder()
    kg_builder.load_pulp_domain_seed_data()
    
    # 创建增强检索器
    retriever = EnhancedRetriever()
    
    # 创建意图分类器
    classifier = IntentClassifier()
    
    # 用户查询
    user_query = "介绍针叶木浆的生产工艺和特点"
    
    print(f"\n用户查询: {user_query}")
    
    # 1. 意图识别
    intent_result = classifier.classify(user_query)
    print(f"\n步骤1 - 意图识别:")
    print(f"  意图类型: {intent_result['intent']}")
    print(f"  置信度: {intent_result['confidence']:.2f}")
    
    # 2. 查询优化
    optimizer = QueryOptimizer(classifier)
    optimized = optimizer.optimize(user_query)
    print(f"\n步骤2 - 查询优化:")
    print(f"  优化后查询: {optimized['optimized_query']}")
    
    # 3. 执行检索
    results = retriever.search(user_query, top_k=5)
    print(f"\n步骤3 - 智能检索:")
    print(f"  找到 {len(results)} 个相关结果")
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n  结果 {i}:")
        print(f"    实体: {result.get('entity_name')}")
        print(f"    类型: {result.get('entity_type')}")
        print(f"    得分: {result.get('final_score', 0):.2f}")
        if result.get('relations'):
            print(f"    关系: {result['relations'][0]}")
    
    # 4. 生成答案
    answer_result = retriever.answer_query(user_query)
    print(f"\n步骤4 - 生成答案:")
    print(f"  {answer_result['answer']}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("纸浆领域知识图谱与智能检索系统演示")
    print("="*60)
    
    try:
        # 1. 知识图谱构建
        kg_builder = demo_knowledge_graph()
        
        # 2. 结构化模式提示器
        prompter = demo_pattern_prompter()
        
        # 3. 数据增强
        augmenter = demo_data_augmentation()
        
        # 4. BART微调
        finetuner = demo_bart_finetuner()
        
        # 5. 增强检索
        retriever = demo_enhanced_retriever()
        
        # 6. 意图分类
        classifier, optimizer = demo_intent_classifier()
        
        # 7. 完整工作流程
        demo_complete_workflow()
        
        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n演示过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

