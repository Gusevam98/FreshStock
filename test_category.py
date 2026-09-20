# test_category.py
"""
Демонстрация работы класса Category
"""

from models.category import Category, CategoryManager

def test_category():
    """Тестирование функциональности категорий"""
    
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ КЛАССА CATEGORY")
    print("=" * 50)
    
    # Создаем менеджер категорий
    manager = CategoryManager()
    
    # Добавляем категории
    print("\n1. Добавление категорий:")
    cat1 = manager.add_category("Электроника", "Электронные устройства и компоненты")
    print(f"   ✓ {cat1}")
    
    cat2 = manager.add_category("Бытовая техника", "Техника для дома")
    print(f"   ✓ {cat2}")
    
    cat3 = manager.add_category("Телефоны", "Мобильные телефоны", parent_id=1)
    print(f"   ✓ {cat3}")
    
    cat4 = manager.add_category("Ноутбуки", "Портативные компьютеры", parent_id=1)
    print(f"   ✓ {cat4}")
    
    # Получаем все категории
    print("\n2. Все категории:")
    for cat in manager.get_all_categories():
        print(f"   - {cat}")
    
    # Получаем подкатегории
    print("\n3. Подкатегории 'Электроника' (ID=1):")
    subcats = manager.get_subcategories(1)
    for cat in subcats:
        print(f"   - {cat}")
    
    # Преобразование в словарь
    print("\n4. Категория в формате словаря:")
    print(f"   {cat1.to_dict()}")
    
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 50)

if __name__ == "__main__":
    test_category()
