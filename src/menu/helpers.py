import os
import json

from models import Category, Position

def clear_screen():
    """Очистка экрана"""
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title):
    """Печать заголовка"""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")

def print_menu_item(num, text, description=""):
    """Печать пункта меню"""
    print(f"{num}. {text}")
    if description:
        print(f"   {description}")

def wait_for_enter():
    """Ожидание нажатия Enter"""
    input("\nНажмите Enter для продолжения...")

def load_test_data(cat_repo, pos_repo, json_path=None):
    if json_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        json_path = os.path.join(os.path.dirname(project_root), 'data', 'test_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = {}
    for cat in data['categories']:
        if 'parent' in cat:
            parent = categories[cat['parent']]
            categories[cat['name']] = cat_repo.add_category(cat['name'], parent.id)
        else:
            categories[cat['name']] = cat_repo.add_category(cat['name'])
    
    for pos in data['positions']:
        pos_repo.add_position(
            category_id=categories[pos['category']].id,
            name=pos['name'],
            weight=pos['weight'],
            calories=pos['calories'],
            protein=pos['protein'],
            fat=pos['fat'],
            carbs=pos['carbs'],
            is_liquid=pos['is_liquid'],
            is_hot=pos['is_hot']
        )

def print_tree(cat_repo, start_category_id=None):
    tree = cat_repo.get_tree(start_category_id)

    for node_type, obj, level in tree:
        indent = "  " * level

        if node_type == "category":
            print(f"{indent}📁 {obj.name} (id: {obj.id})")

        elif node_type == "position":
            liquid = "💧" if obj.is_liquid else ""
            hot = "🔥" if obj.is_hot else ""

            nutritional = ""
            if obj.calories or obj.protein or obj.fat or obj.carbs:
                nutritional = (
                    f" ({obj.calories or 0}ккал,"
                    f" Б:{obj.protein or 0}"
                    f" Ж:{obj.fat or 0}"
                    f" У:{obj.carbs or 0})"
                )

            weight = f" {obj.weight}г" if obj.weight else ""

            print(f"{indent}📄 {obj.name}{liquid}{hot}{weight}{nutritional}")
