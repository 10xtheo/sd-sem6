from database import init_db

from .helpers import clear_screen, print_header, print_menu_item, wait_for_enter, print_tree, load_test_data

def settings_menu(session, cat_repo, pos_repo):
    while True:
        clear_screen()
        print_header("НАСТРОЙКИ")
        
        print_menu_item(1, "Инициализировать базу данных")
        print_menu_item(2, "Загрузить тестовые данные")
        print_menu_item(3, "Очистить базу данных")
        print_menu_item(4, "Показать структуру БД")
        print_menu_item(0, "Вернуться в главное меню")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            clear_screen()
            print_header("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
            
            confirm = input("Это создаст новые таблицы. Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                init_db()
                print("\n✅ База данных инициализирована")
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "2":
            clear_screen()
            print_header("ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ")
            confirm = input("Это добавит тестовые данные. Продолжить? (y/n): ").strip().lower()
            if confirm == 'y':
                try:
                    # Очистка перед загрузкой               
                    pos_repo.delete_all()
                    cat_repo.delete_all()
                    
                    # Загрузка
                    load_test_data(cat_repo, pos_repo)
                    print("\n✅ Тестовые данные загружены!")
                    print_tree(cat_repo)
                    
                except Exception as e:
                    print(f"\n❌ Ошибка: {e}")
                    session.rollback()
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "3":
            clear_screen()
            print_header("ОЧИСТКА БАЗЫ ДАННЫХ")
            
            print("ВНИМАНИЕ! Это удалит ВСЕ данные!")
            confirm = input("Введите 'DELETE ALL' для подтверждения: ").strip()
            
            if confirm == 'DELETE ALL':
                pos_repo.delete_all()
                cat_repo.delete_all()
                print("\n✅ База данных очищена")
            else:
                print("\nОперация отменена")
            
            wait_for_enter()
        
        elif choice == "4":
            clear_screen()
            print_header("СТРУКТУРА БАЗЫ ДАННЫХ")
            
            print("📁 Таблица categories:")
            print("  • id (INTEGER, PRIMARY KEY)")
            print("  • name (VARCHAR(255), NOT NULL)")
            print("  • parent_id (INTEGER, FOREIGN KEY → categories.id)")
            print("  • Индекс: ix_categories_parent_id")
            
            print("\n📄 Таблица positions:")
            print("  • id (INTEGER, PRIMARY KEY)")
            print("  • category_id (INTEGER, FOREIGN KEY → categories.id, NOT NULL)")
            print("  • name (VARCHAR(255), NOT NULL)")
            print("  • weight (SMALLINT)")
            print("  • calories (SMALLINT)")
            print("  • protein (SMALLINT)")
            print("  • fat (SMALLINT)")
            print("  • carbs (SMALLINT)")
            print("  • is_liquid (BOOLEAN, default=False)")
            print("  • is_hot (BOOLEAN, default=False)")
            print("  • Индекс: ix_positions_category_id")
            
            wait_for_enter()
        
        elif choice == "0":
            break
