"""
数据增强模块 - 用于扩充训练数据
解决领域标注数据稀疏问题
"""
from typing import List, Dict, Any, Optional
import random
import re
from copy import deepcopy


class DataAugmentation:
    """数据增强器"""
    
    def __init__(self):
        # 纸浆领域同义词词典
        self.synonyms = {
            "纸浆": ["浆料", "浆液", "纸浆纤维"],
            "白度": ["亮度", "白值"],
            "强度": ["抗张强度", "断裂强度"],
            "纤维长度": ["纤维平均长度", "长度"],
            "蒸煮": ["蒸解", "碱蒸煮"],
            "漂白": ["漂白处理", "化学漂白"],
            "洗涤": ["清洗", "水洗"],
            "针叶木": ["针叶材", "针叶树"],
            "阔叶木": ["阔叶材", "阔叶树"],
            "机械浆": ["机械纸浆", "高得率浆"],
            "化学浆": ["化学纸浆", "碱法制浆"],
        }
        
        # 纸浆领域相关词
        self.related_terms = {
            "纸浆": ["造纸", "纸张", "纤维素", "木浆"],
            "针叶木浆": ["松木浆", "杉木浆", "针叶材浆"],
            "阔叶木浆": ["桉木浆", "杨木浆", "阔叶材浆"],
            "强度": ["撕裂度", "耐破度", "环压强度"],
            "白度": ["ISO白度", "蓝光白度", "CIE白度"],
        }
    
    def synonym_replacement(self, text: str, replacement_ratio: float = 0.3) -> str:
        """同义词替换"""
        words = text.split()
        num_replacements = int(len(words) * replacement_ratio)
        
        indices_to_replace = random.sample(range(len(words)), min(num_replacements, len(words)))
        
        augmented_text = words.copy()
        for idx in indices_to_replace:
            word = words[idx]
            if word in self.synonyms:
                synonym = random.choice(self.synonyms[word])
                augmented_text[idx] = synonym
        
        return ' '.join(augmented_text)
    
    def random_insertion(self, text: str, num_insertions: int = 2) -> str:
        """随机插入"""
        words = text.split()
        
        for _ in range(num_insertions):
            if not words:
                break
            
            # 找到具有同义词的词
            eligible_words = [w for w in words if w in self.synonyms]
            if not eligible_words:
                break
            
            random_word = random.choice(eligible_words)
            synonym = random.choice(self.synonyms[random_word])
            
            # 随机插入位置
            insert_pos = random.randint(0, len(words))
            words.insert(insert_pos, synonym)
        
        return ' '.join(words)
    
    def random_deletion(self, text: str, deletion_ratio: float = 0.2) -> str:
        """随机删除"""
        words = text.split()
        
        if len(words) <= 3:
            return text
        
        num_deletions = int(len(words) * deletion_ratio)
        indices_to_delete = random.sample(range(len(words)), min(num_deletions, len(words) - 3))
        
        augmented_text = [w for i, w in enumerate(words) if i not in indices_to_delete]
        
        return ' '.join(augmented_text)
    
    def swap_words(self, text: str, num_swaps: int = 2) -> str:
        """交换词顺序"""
        words = text.split()
        
        if len(words) <= 1:
            return text
        
        for _ in range(num_swaps):
            if len(words) < 2:
                break
            
            idx1, idx2 = random.sample(range(len(words)), 2)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ' '.join(words)
    
    def paraphrase(self, text: str) -> str:
        """改写（使用领域特定的改写规则）"""
        paraphrased = text
        
        # 规则1: 改变表达方式
        paraphrases = {
            r"具有(\w+)特征": r"呈现出\1特点",
            r"(\w+)达到(\w+)": r"\1为\2",
            r"(\w+)用于(\w+)": r"\1应用于\2",
            r"(\w+)主要由(\w+)组成": r"\1的主要成分是\2",
        }
        
        for pattern, replacement in paraphrases.items():
            paraphrased = re.sub(pattern, replacement, paraphrased)
        
        return paraphrased
    
    def augment(self, text: str, methods: Optional[List[str]] = None) -> List[str]:
        """应用多种增强方法"""
        if methods is None:
            methods = ['synonym_replacement', 'random_insertion', 'random_deletion', 'swap_words', 'paraphrase']
        
        augmented_texts = []
        
        for method in methods:
            try:
                if method == 'synonym_replacement':
                    augmented_texts.append(self.synonym_replacement(text))
                elif method == 'random_insertion':
                    augmented_texts.append(self.random_insertion(text))
                elif method == 'random_deletion':
                    augmented_texts.append(self.random_deletion(text))
                elif method == 'swap_words':
                    augmented_texts.append(self.swap_words(text))
                elif method == 'paraphrase':
                    augmented_texts.append(self.paraphrase(text))
            except Exception as e:
                print(f"增强方法 {method} 失败: {e}")
        
        return augmented_texts
    
    def augment_triples(self, triples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """增强三元组数据"""
        augmented_triples = []
        
        for triple in triples:
            augmented_triples.append(triple)
            
            # 同义词替换增强
            if triple['subject'] in self.synonyms:
                synonym = random.choice(self.synonyms[triple['subject']])
                new_triple = deepcopy(triple)
                new_triple['subject'] = synonym
                augmented_triples.append(new_triple)
            
            if triple['object'] in self.synonyms:
                synonym = random.choice(self.synonyms[triple['object']])
                new_triple = deepcopy(triple)
                new_triple['object'] = synonym
                augmented_triples.append(new_triple)
        
        return augmented_triples
    
    def augment_entity_texts(self, entity_texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """增强实体文本"""
        augmented_texts = []
        
        for entity_text in entity_texts:
            # 添加原始文本
            augmented_texts.append(entity_text)
            
            # 生成增强版本
            text = entity_text.get('text', '')
            if text:
                augmented = self.augment(text, methods=['synonym_replacement', 'paraphrase'])
                for aug_text in augmented:
                    new_entity_text = deepcopy(entity_text)
                    new_entity_text['text'] = aug_text
                    new_entity_text['source'] = 'augmented'
                    augmented_texts.append(new_entity_text)
        
        return augmented_texts
    
    def generate_synthetic_examples(self, seed_data: List[Dict[str, Any]], num_samples: int = 100) -> List[Dict[str, Any]]:
        """生成合成示例"""
        synthetic_examples = []
        
        # 纸浆领域模板
        templates = [
            "{entity}是一种{type}，具有{attribute}特征。",
            "{entity}的{attribute}为{value}。",
            "{entity}广泛应用于{application}领域。",
            "{entity}通过{process}工艺制成。",
            "{entity}的主要成分包括{components}。",
        ]
        
        # 从种子数据中提取信息
        for _ in range(num_samples):
            seed = random.choice(seed_data)
            
            template = random.choice(templates)
            
            # 填充模板
            synthetic_text = template.format(
                entity=seed.get('entity_name', '纸浆'),
                type=seed.get('entity_type', '纸浆产品'),
                attribute=random.choice(['白度', '强度', '纤维长度']),
                value=random.choice(['80-90', '高', '中等']),
                application=random.choice(['造纸', '印刷', '包装']),
                process=random.choice(['蒸煮', '漂白', '洗涤']),
                components=random.choice(['纤维素', '半纤维素', '木质素'])
            )
            
            synthetic_examples.append({
                'text': synthetic_text,
                'source': 'synthetic',
                'seed_id': seed.get('entity_id')
            })
        
        return synthetic_examples
    
    def add_noise(self, text: str, noise_ratio: float = 0.1) -> str:
        """添加噪声（模拟不完美标注）"""
        chars = list(text)
        num_changes = int(len(chars) * noise_ratio)
        
        change_indices = random.sample(range(len(chars)), min(num_changes, len(chars)))
        
        for idx in change_indices:
            # 随机选择：删除、替换或插入
            action = random.choice(['delete', 'replace', 'insert'])
            
            if action == 'delete' and len(chars) > 1:
                chars.pop(idx)
            elif action == 'replace':
                chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
            elif action == 'insert':
                chars.insert(idx, random.choice('abcdefghijklmnopqrstuvwxyz'))
        
        return ''.join(chars)

