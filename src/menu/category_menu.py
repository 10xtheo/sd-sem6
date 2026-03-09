from tabulate import tabulate

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter, print_tree


# TODO убрать сессию и репы
def category_menu(session, cat_repo, pos_repo):
    """Меню операций с категориями"""
    while True:
        clear_screen()
        print_header("ОПЕРАЦИИ С КАТЕГОРИЯМИ")
        
        print_menu_item(1, "Показать все категории")
        print_menu_item(2, "Показать дерево категорий")
        print_menu_item(3, "Добавить категорию")
        print_menu_item(4, "Переместить категорию")
        print_menu_item(5, "Переименовать категорию")
        print_menu_item(6, "Удалить категорию")
        print_menu_item(7, "Найти потомков категории")
        print_menu_item(8, "Найти родителей категории")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ВСЕ КАТЕГОРИИ")
            # todo encapsulate repo logic
            categories = cat_repo.get_all_categories()
            if categories:
                table = [[c.id, c.name, c.parent_id or "Корень"] for c in categories]
                print(tabulate(table, headers=["ID", "Название", "Родитель"], tablefmt="grid"))
            else:
                print("Категории отсутствуют")
            
            wait_for_enter()
        # todo remove session from here - encapsulate
        elif choice == "2":
            clear_screen()
            print_header("ДЕРЕВО КАТЕГОРИЙ")
            print_tree(session)
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("ДОБАВЛЕНИЕ КАТЕГОРИИ")
            
            name = input("Название категории: ").strip()
            # todo remove repo
            # Показываем существующие категории для выбора родителя
            categories = cat_repo.get_all_categories()
            if categories:
                print("\nСуществующие категории:")
                for cat in categories:
                    print(f"  ID: {cat.id} - {cat.name}")
            
            parent_id = input("\nID родительской категории (Enter для корня): ").strip()
            parent_id = int(parent_id) if parent_id else None
            # todo repo remove
            try:
                category = cat_repo.add_category(name, parent_id)
                print(f"\n✅ Категория добавлена с ID: {category.id}")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("ПЕРЕМЕЩЕНИЕ КАТЕГОРИИ")
            
            # Показываем дерево
            print_tree(session)
            
            category_id = input("\nID перемещаемой категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            new_parent_id = input("ID нового родителя (Enter для корня): ").strip()
            new_parent_id = int(new_parent_id) if new_parent_id else None
            
            try:
                cat_repo.move_category(int(category_id), new_parent_id)
                print("\n✅ Категория перемещена")
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
            
            wait_for_enter()
        
        elif choice == "5":
            clear_screen()
            print_header("ПЕРЕИМЕНОВАНИЕ КАТЕГОРИИ")
            
            # Показываем список категорий
            categories = cat_repo.get_all_categories()
            if categories:
                table = [[c.id, c.name] for c in categories]
                print(tabulate(table, headers
                =["ID", "Название"], tablefmt="grid"))
            else:
                print("Категории отсутствуют")
                wait_for_enter()
                continue
            
            category_id = input("\nID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            new_name = input("Новое название: ").strip()
            
            ok, message, category = cat_repo.update_category(int(category_id), name=new_name)
            if ok:
                print(f"\n✅ Категория переименована, новое имя: {category.name}")
            else:
                print(f"\n❌ Ошибка: {message}")
            
            wait_for_enter()
        
        elif choice == "6":
            clear_screen()
            print_header("УДАЛЕНИЕ КАТЕГОРИИ")
            
            # Показываем дерево
            print_tree(session)
            
            category_id = input("\nID удаляемой категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            cascade = input("Удалить с подкатегориями и позициями? (y/n): ").strip().lower() == 'y'
            confirm = input("Подтвердите удаление (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                try:
                    cat_repo.delete_category(int(category_id), cascade)
                    print("\n✅ Категория удалена")
                except Exception as e:
                    print(f"\n❌ Ошибка: {e}")
            else:
                print("\nУдаление отменено")
            
            wait_for_enter()
        
        elif choice == "7":
            clear_screen()
            print_header("ПОИСК ПОТОМКОВ")
            
            category_id = input("ID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            category = cat_repo.get_category(int(category_id))
            if not category:
                print("\n❌ Категория не найдена")
                wait_for_enter()
                continue
            
            descendants = category.get_all_descendants(session)
            if descendants:
                print(f"\nПотомки категории '{category.name}':")
                for desc in descendants:
                    # indent = "  " * (desc.level - 1)
                    indent = "  "
                    print(f"{indent}• {desc.name}")
            else:
                print("\nНет потомков")
            
            wait_for_enter()
        
        elif choice == "8":
            clear_screen()
            print_header("ПОИСК РОДИТЕЛЕЙ")
            
            category_id = input("ID категории: ").strip()
            if not category_id.isdigit():
                print("❌ Некорректный ID")
                wait_for_enter()
                continue
            
            # Простой поиск родителей (можно расширить для рекурсивного)
            category = cat_repo.get_category(int(category_id))
            if not category:
                print("\n❌ Категория не найдена")
                wait_for_enter()
                continue
            
            if category.parent:
                print(f"\nРодитель категории '{category.name}':")
                print(f"  {category.parent.name} (ID: {category.parent.id})")
                
                # Поиск всех родителей (рекурсивно)
                parents = []
                current = category.parent
                while current:
                    parents.append(current)
                    current = current.parent
                
                if len(parents) > 1:
                    print("\nВсе родители:")
                    for i, p in enumerate(reversed(parents)):
                        indent = "  " * i
                        print(f"{indent}• {p.name}")
            else:
                print(f"\nКатегория '{category.name}' является корневой")
            
            wait_for_enter()
        
        elif choice == "0":
            break