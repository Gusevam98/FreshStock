# models/category.py
"""
Модель категории товаров для системы учета склада
"""

class Category:
    """Класс для управления категориями товаров"""
    
    def __init__(self, id=None, name="", description="", parent_id=None):
        """
        Инициализация категории
        
        Args:
            id: Уникальный идентификатор категории
            name: Название категории
            description: Описание категории
            parent_id: ID родительской категории (для вложенности)
        """
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id
    
    def __str__(self):
        """Строковое представление категории"""
        return f"Категория(id={self.id}, name='{self.name}')"
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание объекта из словаря"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            parent_id=data.get('parent_id')
        )


class CategoryManager:
    """Менеджер для управления категориями"""
    
    def __init__(self):
        """Инициализация менеджера категорий"""
        self.categories = []
        self.next_id = 1
    
    def add_category(self, name, description="", parent_id=None):
        """
        Добавление новой категории
        
        Args:
            name: Название категории
            description: Описание
            parent_id: ID родительской категории
            
        Returns:
            Category: Созданная категория
        """
        category = Category(
            id=self.next_id,
            name=name,
            description=description,
            parent_id=parent_id
        )
        self.categories.append(category)
        self.next_id += 1
        return category
    
    def get_category(self, category_id):
        """Получение категории по ID"""
        for category in self.categories:
            if category.id == category_id:
                return category
        return None
    
    def get_all_categories(self):
        """Получение всех категорий"""
        return self.categories
    
    def delete_category(self, category_id):
        """Удаление категории по ID"""
        for i, category in enumerate(self.categories):
            if category.id == category_id:
                return self.categories.pop(i)
        return None
    
    def get_subcategories(self, parent_id):
        """Получение всех подкатегорий для родительской категории"""
        return [c for c in self.categories if c.parent_id == parent_id]