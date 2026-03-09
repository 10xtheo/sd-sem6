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

# TODO: перенести работу с сессией из main
def print_tree(session, start_category_id=None, level=0):
    """Рекурсивный вывод дерева категорий"""
    query = session.query(Category)
    if start_category_id is None:
        categories = query.filter(Category.parent_id.is_(None)).order_by(Category.id).all()
    else:
        categories = query.filter(Category.parent_id == start_category_id).order_by(Category.id).all()
    
    for cat in categories:
        indent = "  " * level
        print(f"{indent}📁 {cat.name} (id: {cat.id})")
        
        # Вывод позиций категории
        positions = session.query(Position).filter(Position.category_id == cat.id).all()
        for pos in positions:
            liquid = "💧" if pos.is_liquid else ""
            hot = "🔥" if pos.is_hot else ""
            nutritional = ""
            if pos.calories or pos.protein or pos.fat or pos.carbs:
                nutritional = f" ({pos.calories or 0}ккал, Б:{pos.protein or 0} Ж:{pos.fat or 0} У:{pos.carbs or 0})"
            weight = f" {pos.weight}г" if pos.weight else ""
            print(f"{indent}  📄 {pos.name}{liquid}{hot}{weight}{nutritional}")
        
        # Рекурсивный вывод подкатегорий
        print_tree(session, cat.id, level + 1)

def load_test_data(cat_repo, pos_repo, json_path=None):
    if json_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))  # src/menu/helpers
        project_root = os.path.dirname(current_dir)
        json_path = os.path.join(os.path.dirname(project_root), 'data', 'test_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create categories and store in dict for lookup
    categories = {}
    for cat in data['categories']:
        if 'parent' in cat:
            parent = categories[cat['parent']]
            categories[cat['name']] = cat_repo.add_category(cat['name'], parent.id)
        else:
            categories[cat['name']] = cat_repo.add_category(cat['name'])
    
    # Create positions
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

