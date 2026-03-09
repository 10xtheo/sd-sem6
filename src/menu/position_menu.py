from tabulate import tabulate

from models import Position

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter, print_tree


def position_menu(session, cat_repo, pos_repo):
    """Меню операций с позициями"""
    while True:
        clear_screen()
        print_header("ОПЕРАЦИИ С ПОЗИЦИЯМИ")
        
        print_menu_item(1, "Показать все позиции")
        print_menu_item(2, "Показать позиции категории")
        print_menu_item(3, "Добавить позицию")
        print_menu_item(4, "Редактировать позицию")
        print_menu_item(5, "Переместить позицию в другую категорию")
        print_menu_item(6, "Удалить позицию")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ВСЕ ПОЗИЦИИ")
            
            positions = session.query(Position).all()
            if positions:
                table = []
                for p in positions:
                    liquid = "Да" if p.is_liquid else "Нет"
                    hot = "Да" if p.is_hot else "Нет"
                    table.append([
                        p.id, p.name, p.category.name if p.category else "—",
                        p.weight or "—", p.calories or "—", 
                        f"{p.protein or 0}/{p.fat or 0}/{p.carbs or 0}",
                        liquid, hot
                    ])
                print(tabulate(table, 
                              headers=["ID", "Название", "Категория", "Вес", "Ккал", "Б/Ж/У", "Жидкое", "Горячее"], 
                              tablefmt="grid"))
            else:
                print("Позиции отсутствуют")
            
            wait_for_enter()
        
        elif choice == "2":
            clear_screen()
            print_header("ПОЗИЦИИ КАТЕГОРИИ")
            
            # Показываем дерево для выбора категории
            print_tree(session)
            
            category_id = input("\nID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            positions = pos_repo.get_positions_by_category(int(category_id))
            if positions:
                category = cat_repo.get_category(int(category_id))
                print(f"\nПозиции в категории '{category.name}':")
                table = []
                for p in positions:
                    liquid = "💧" if p.is_liquid else ""
                    hot = "🔥" if p.is_hot else ""
                    table.append([
                        p.id, p.name, p.weight or "—", p.calories or "—",
                        f"{p.protein or 0}/{p.fat or 0}/{p.carbs or 0}",
                        f"{liquid}{hot}"
                    ])
                print(tabulate(table, 
                              headers=["ID", "Название", "Вес", "Ккал", "Б/Ж/У", "Свойства"], 
                              tablefmt="grid"))
            else:
                print("\nВ этой категории нет позиций")
            
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("ДОБАВЛЕНИЕ ПОЗИЦИИ")
            
            # Показываем дерево для выбора категории
            print_tree(session)
            
            category_id = input("\nID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            name = input("Название позиции: ").strip()
            
            print("\nПищевая ценность (Enter для пропуска):")
            weight = input("Вес (граммы): ").strip()
            weight = int(weight) if weight else None
            
            calories = input("Калорийность (ккал): ").strip()
            calories = int(calories) if calories else None
            
            protein = input("Белки (г): ").strip()
            protein = int(protein) if protein else None
            
            fat = input("Жиры (г): ").strip()
            fat = int(fat) if fat else None
            
            carbs = input("Углеводы (г): ").strip()
            carbs = int(carbs) if carbs else None
            
            is_liquid = input("Жидкое? (y/n): ").strip().lower() == 'y'
            is_hot = input("Горячее? (y/n): ").strip().lower() == 'y'
            
            try:
                position = pos_repo.add_position(
                    category_id=int(category_id),
                    name=name,
                    weight=weight,
                    calories=calories,
                    protein=protein,
                    fat=fat,
                    carbs=carbs,
                    is_liquid=is_liquid,
                    is_hot=is_hot
                )
                print(f"\n✅ Позиция добавлена с ID: {position.id}")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("РЕДАКТИРОВАНИЕ ПОЗИЦИИ")
            
            position_id = input("ID позиции: ").strip()
            if not position_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            position = pos_repo.get_position(int(position_id))
            if not position:
                print("\n❌ Позиция не найдена")
                wait_for_enter()
                continue
            
            print(f"\nРедактирование: {position.name}")
            print("(Enter для сохранения текущего значения)\n")
            
            name = input(f"Название [{position.name}]: ").strip()
            if name:
                position.name = name
            
            weight = input(f"Вес [{position.weight or '—'}]: ").strip()
            if weight:
                position.weight = int(weight)
            
            calories = input(f"Калорийность [{position.calories or '—'}]: ").strip()
            if calories:
                position.calories = int(calories)
            
            protein = input(f"Белки [{position.protein or '—'}]: ").strip()
            if protein:
                position.protein = int(protein)
            
            fat = input(f"Жиры [{position.fat or '—'}]: ").strip()
            if fat:
                position.fat = int(fat)
            
            carbs = input(f"Углеводы [{position.carbs or '—'}]: ").strip()
            if carbs:
                position.carbs = int(carbs)
            
            liquid_str = "да" if position.is_liquid else "нет"
            liquid_input = input(f"Жидкое? [{liquid_str}]: ").strip().lower()
            if liquid_input:
                position.is_liquid = liquid_input == 'y' or liquid_input == 'да'
            
            hot_str = "да" if position.is_hot else "нет"
            hot_input = input(f"Горячее? [{hot_str}]: ").strip().lower()
            if hot_input:
                position.is_hot = hot_input == 'y' or hot_input == 'да'
            
            session.commit()
            print("\n✅ Позиция обновлена")
            
            wait_for_enter()
        
        elif choice == "5":
            clear_screen()
            print_header("ПЕРЕМЕЩЕНИЕ ПОЗИЦИИ")
            
            position_id = input("ID позиции: ").strip()
            if not position_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            position = pos_repo.get_position(int(position_id))
            if not position:
                print("\n❌ Позиция не найдена")
                wait_for_enter()
                continue
            
            print(f"\nТекущая категория: {position.category.name}")
            print("\nДоступные категории:")
            print_tree(session)
            
            new_category_id = input("\nID новой категории: ").strip()
            if not new_category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            try:
                pos_repo.move_position(int(position_id), int(new_category_id))
                print("\n✅ Позиция перемещена")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
            
            wait_for_enter()
        
        elif choice == "6":
            clear_screen()
            print_header("УДАЛЕНИЕ ПОЗИЦИИ")
            
            position_id = input("ID позиции: ").strip()
            if not position_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            position = pos_repo.get_position(int(position_id))
            if not position:
                print("\n❌ Позиция не найдена")
                wait_for_enter()
                continue
            
            print(f"\nПозиция: {position.name}")
            confirm = input("Подтвердите удаление (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                try:
                    pos_repo.delete_position(int(position_id))
                    print("\n✅ Позиция удалена")
                except Exception as e:
                    print(f"\n❌ Ошибка: {e}")
            else:
                print("\nУдаление отменено")
            
            wait_for_enter()
        
        elif choice == "0":
            break
