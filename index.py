import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import minimize
from adjustText import adjust_text
import random

class DietNutritionAnalyzer:
    def __init__(self, dishes_data):
        self.dishes = dishes_data['dishes']
        self.calculate_dish_scores()
    
    def calculate_cd_ndi(self, nutrition_dict):
        """计算CD-NDI营养质量指标"""
        protein = nutrition_dict['protein']
        fiber = nutrition_dict['dietaryFiber']
        sat_fat = nutrition_dict['saturatedFat']
        sodium = nutrition_dict['sodium']
        added_sugar = nutrition_dict['addedSugar']
        
        cd_ndi = (protein * 2.5 + fiber * 1.8) - (sat_fat * 3.5 + sodium * 0.01 + added_sugar * 2.5)

        return cd_ndi
    
    def _replace_main_ingredient_name(self, dish):
        """将主料自动替换成具体食材名称"""
        cat = dish.get('category', '')
        replacements = {
            "猪肉类": "猪肉",
            "鸡肉类": "鸡肉",
            "牛肉类": "牛肉",
            "羊肉类": "羊肉",
            "水产类": "鱼肉",
            "蔬菜类": "青菜",
            "豆制品类": "豆腐",
            "汤品类": "汤底",
            "主食类": "米饭",
            "饮品": "饮品基底",
            "小吃油炸": "油炸制品",
            "西式快餐": "鸡排",
            "台式便当": "便当主料",
            "风味快餐": "烤肉",
            "西式简餐": "芝士",
        }
        default_name = replacements.get(cat, "未知食材")
        
        # 遍历 ingredients
        for ing in dish.get('ingredients', []):
            if ing['name'] == "主料":
                ing['name'] = default_name
    
    def calculate_dish_scores(self):
        """为每个菜品计算营养得分和综合得分"""
        for dish in self.dishes:
            # 计算CD-NDI
            dish['cd_ndi'] = self.calculate_cd_ndi(dish['total_nutrition'])
            
            # 标准化营养得分和喜爱度得分（0-1范围）
            scaler = MinMaxScaler()
            
            # 营养得分（CD-NDI越高越好）
            nutrition_score = dish['cd_ndi']
            
            # 喜爱度得分
            popularity_score = dish['popularity_score']
            
            dish['nutrition_score'] = nutrition_score
            dish['normalized_popularity'] = popularity_score / 10.0  # 标准化到0-1
            
            # 综合匹配度得分（平衡营养和喜爱度）
            # 权重可调整：0.6营养 + 0.4喜爱度
            dish['match_score'] = 0.6 * (nutrition_score / 100) + 0.4 * dish['normalized_popularity']
    
    def analyze_correlation(self):
        """分析营养得分与喜爱度的相关性"""
        nutrition_scores = [dish['nutrition_score'] for dish in self.dishes]
        popularity_scores = [dish['popularity_score'] for dish in self.dishes]
        
        correlation = np.corrcoef(nutrition_scores, popularity_scores)[0, 1]
        return correlation
    
    def find_optimal_combination(self, daily_calorie_limit=2000):
        """找到最优菜品组合（营养与喜爱度的平衡）"""
        # 简化版：选择前N个菜品使得总匹配度最高
        dishes_sorted = sorted(self.dishes, key=lambda x: x['match_score'], reverse=True)
        
        # 模拟选择（实际应用可扩展为线性规划）
        selected_dishes = dishes_sorted[:5]  # 选择前5个最高匹配度菜品
        
        return selected_dishes
    
    def analyze_ingredient_frequency(self):
        """分析主料使用频率"""
        ingredient_count = {}
        for dish in self.dishes:
            for ing in dish['ingredients']:
                name = ing['name']
                ingredient_count[name] = ingredient_count.get(name, 0) + 1
        
        # 按频率排序
        sorted_ingredients = sorted(ingredient_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_ingredients
    
    def visualize_analysis_optimized(self, aggregation_method='average'):
        """
        优化版可视化分析
        
        Parameters:
        aggregation_method: 'average'（平均值）或 'frequency'（带频率）
        """
        # 处理主料名称
        for dish in self.dishes:
            self._replace_main_ingredient_name(dish)
        
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(20, 14))
        texts = []

        # === 食材数据聚合 ===
        ingredient_stats = {}
        
        for dish in self.dishes:
            for ing in dish.get('ingredients', []):
                name = ing['name']
                health = self.calculate_cd_ndi(ing)
                pop = dish['popularity_score']
                
                if name not in ingredient_stats:
                    ingredient_stats[name] = {'healths': [], 'pops': []}
                ingredient_stats[name]['healths'].append(health)
                ingredient_stats[name]['pops'].append(pop)
        
        # 根据聚合方法处理数据
        if aggregation_method == 'average':
            # 平均值聚合
            ingredient_health = []
            ingredient_pop = []
            ingredient_names = []
            
            for name, stats in ingredient_stats.items():
                avg_health = np.mean(stats['healths'])
                avg_pop = np.mean(stats['pops'])
                
                ingredient_health.append(avg_health)
                ingredient_pop.append(avg_pop)
                ingredient_names.append(name)
            
            # 绘制食材点
            ax.scatter(ingredient_health, ingredient_pop, 
                       s=35, c='limegreen', alpha=0.7, label='原材料')
        
        elif aggregation_method == 'frequency':
            # 频率加权聚合
            ingredient_health = []
            ingredient_pop = []
            ingredient_names = []
            sizes = []
            
            for name, stats in ingredient_stats.items():
                avg_health = np.mean(stats['healths'])
                avg_pop = np.mean(stats['pops'])
                frequency = len(stats['healths'])
                
                ingredient_health.append(avg_health)
                ingredient_pop.append(avg_pop)
                ingredient_names.append(name)
                sizes.append(30 + frequency * 8)  # 大小与频率成正比
            
            scatter = ax.scatter(ingredient_health, ingredient_pop, 
                               s=sizes, c='limegreen', alpha=0.7, 
                               label='原材料（点大小=使用频率）')

        # === 菜品数据（保持不变）===
        dish_nutrition = [dish['nutrition_score'] for dish in self.dishes]
        dish_popularity = [dish['popularity_score'] for dish in self.dishes]
        dish_names = [dish['name'] for dish in self.dishes]

        ax.scatter(dish_nutrition, dish_popularity, s=60, c='royalblue', alpha=0.8, label='菜品')

        # === 添加标签 ===
        # 食材标签
        for i, name in enumerate(ingredient_names):
            texts.append(ax.text(ingredient_health[i], ingredient_pop[i], name,
                                fontsize=8, color='darkgreen', alpha=0.8))
        
        # 菜品标签
        for i, name in enumerate(dish_names):
            texts.append(ax.text(dish_nutrition[i], dish_popularity[i], name,
                                fontsize=9, color='navy', alpha=0.9, weight='bold'))

        # === 自动避让 ===
        adjust_text(
            texts,
            expand_text=(1.3, 1.5),
            expand_points=(1.3, 1.5),
            force_text=1.2,
            force_points=0.8,
            arrowprops=dict(arrowstyle='-', color='gray', lw=0.4, alpha=0.6),
            only_move={'points': 'xy', 'text': 'xy'},  # 双方向避让
            precision=0.03,
            max_iter=800  # 更多迭代让布局更精确
        )

        # === 图表样式 ===
        ax.set_xlabel('健康值 (CD-NDI)', fontsize=14)
        ax.set_ylabel('喜爱度', fontsize=14)
        ax.set_title('好感度与健康度匹配分析', fontsize=16)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=12)

        plt.tight_layout()
        plt.show()
    
    def generate_recommendations(self):
        """生成优化建议"""
        correlation = self.analyze_correlation()
        
        print("=== 学生膳食营养与喜爱度匹配分析报告 ===")
        print(f"营养得分与喜爱度相关性: {correlation:.3f}")
        
        if correlation < -0.3:
            print("分析结果: 存在明显的营养-喜爱度背离现象")
            print("💡💡 建议: 需要重点改进高营养菜品的口味吸引力")
        elif correlation > 0.3:
            print("分析结果: 营养与喜爱度呈现正相关")
            print("💡💡 建议: 当前菜品设计较为合理，可继续优化")
        else:
            print("分析结果: 营养与喜爱度关联性较弱")
            print("建议: 需要系统性优化菜品设计")
        
        print("\n🏆🏆 匹配度最高菜品TOP5:")
        dishes_sorted = sorted(self.dishes, key=lambda x: x['match_score'], reverse=True)
        for i, dish in enumerate(dishes_sorted[:5]):
            print(f"{i+1}. {dish['name']} (匹配度: {dish['match_score']:.3f})")
        
        print("\n📈📈 各类别表现分析:")
        categories = list(set([dish['category'] for dish in self.dishes]))
        for category in categories:
            cat_dishes = [dish for dish in self.dishes if dish['category'] == category]
            avg_match = np.mean([dish['match_score'] for dish in cat_dishes])
            avg_popularity = np.mean([dish['popularity_score'] for dish in cat_dishes])
            print(f"{category}: 平均匹配度{avg_match:.3f}, 平均喜爱度{avg_popularity:.1f}")
        
        # 新增：食材使用频率分析
        print("\n🥩🥬 食材使用频率分析:")
        ingredient_freq = self.analyze_ingredient_frequency()
        for i, (ingredient, count) in enumerate(ingredient_freq[:10]):  # 显示前10个
            print(f"{i+1}. {ingredient}: 使用{count}次")

# 使用示例
if __name__ == "__main__":
    # 加载数据（这里直接使用上面提供的JSON数据）
    # 注意：这里需要将文档1的内容保存为datas.json文件
    with open('datas.json', 'r', encoding='utf-8') as f:
        dishes_data = json.load(f)
    
    # 创建分析器
    analyzer = DietNutritionAnalyzer(dishes_data)
    
    # 生成分析报告
    analyzer.generate_recommendations()
    
    # 可视化分析（使用聚合方法）
    print("\n📊📊 可视化分析（食材聚合显示）...")
    analyzer.visualize_analysis_optimized(aggregation_method='average')
    
    # 找到最优组合
    optimal_dishes = analyzer.find_optimal_combination()
    print("\n🎯🎯 推荐每日菜品组合:")
    for i, dish in enumerate(optimal_dishes):
        print(f"{i+1}. {dish['name']} (营养: {dish['cd_ndi']:.1f}, 喜爱度: {dish['popularity_score']})")