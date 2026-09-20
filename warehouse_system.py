import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Часть 1: Модель данных (Работа с БД)

class Database:
    def __init__(self, db_name="warehouse.db"):
        """Инициализация подключения к базе данных"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Создание таблиц"""
        # Таблица товаров
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT,
                unit TEXT DEFAULT 'шт',
                quantity INTEGER DEFAULT 0,
                price REAL DEFAULT 0,
                min_quantity INTEGER DEFAULT 10,
                location TEXT
            )
        """)

        # Таблица операций (приход/расход)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                operation_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                operation_date TEXT,
                comment TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)

        # Таблица контрагентов
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT,
                contact TEXT
            )
        """)

        self.conn.commit()

    # === Товары ===
    def add_product(self, article, name, category, unit, quantity, price, min_qty, location):
        try:
            self.cursor.execute("""
                INSERT INTO products (article, name, category, unit, quantity, price, min_quantity, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (article, name, category, unit, quantity, price, min_qty, location))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return self.cursor.fetchone()

    def update_product_quantity(self, product_id, new_quantity):
        self.cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.conn.commit()

    def get_low_stock_products(self):
        self.cursor.execute("SELECT * FROM products WHERE quantity <= min_quantity")
        return self.cursor.fetchall()

    # === Операции ===
    def add_operation(self, product_id, op_type, quantity, comment):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO operations (product_id, operation_type, quantity, operation_date, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, op_type, quantity, date_now, comment))
        self.conn.commit()

    def get_all_operations(self):
        self.cursor.execute("""
            SELECT o.id, p.article, p.name, o.operation_type, o.quantity, o.operation_date, o.comment
            FROM operations o
            JOIN products p ON o.product_id = p.id
            ORDER BY o.operation_date DESC
        """)
        return self.cursor.fetchall()

    # === Контрагенты ===
    def add_partner(self, name, p_type, contact):
        self.cursor.execute("INSERT INTO partners (name, type, contact) VALUES (?, ?, ?)", (name, p_type, contact))
        self.conn.commit()

    def get_all_partners(self):
        self.cursor.execute("SELECT * FROM partners")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Часть 2: Интерфейс (GUI)

class WarehouseApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("ИС «FreshStock» - Учет товаров")
        self.root.geometry("1100x700")

        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Вкладка 1: Каталог товаров
        self.frame_products = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_products, text="Каталог товаров")
        self.setup_products_tab()

        # Вкладка 2: Приход товара
        self.frame_income = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_income, text="Приход")
        self.setup_income_tab()

        # Вкладка 3: Расход товара
        self.frame_expense = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_expense, text="Расход")
        self.setup_expense_tab()

        # Вкладка 4: История операций
        self.frame_history = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_history, text="История операций")
        self.setup_history_tab()

        # Вкладка 5: Отчеты
        self.frame_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_reports, text="Отчеты")
        self.setup_reports_tab()

        self.refresh_data()

    def setup_products_tab(self):
        # Форма добавления товара
        lbl_frame = ttk.LabelFrame(self.frame_products, text="Добавить новый товар")
        lbl_frame.pack(padx=10, pady=10, fill="x")

        # Первая строка
        ttk.Label(lbl_frame, text="Артикул:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_article = ttk.Entry(lbl_frame, width=15)
        self.entry_article.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Название:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_name = ttk.Entry(lbl_frame, width=25)
        self.entry_name.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Категория:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_category = ttk.Entry(lbl_frame, width=15)
        self.entry_category.grid(row=0, column=5, padx=5, pady=5)

        # Вторая строка
        ttk.Label(lbl_frame, text="Ед. изм.:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_unit = ttk.Entry(lbl_frame, width=10)
        self.entry_unit.insert(0, "шт")
        self.entry_unit.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Кол-во:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_quantity = ttk.Entry(lbl_frame, width=10)
        self.entry_quantity.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Цена за кг:").grid(row=1, column=4, padx=5, pady=5)
        self.entry_price = ttk.Entry(lbl_frame, width=10)
        self.entry_price.grid(row=1, column=5, padx=5, pady=5)

        # Третья строка
        ttk.Label(lbl_frame, text="Мин. остаток:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_min_qty = ttk.Entry(lbl_frame, width=10)
        self.entry_min_qty.insert(0, "10")
        self.entry_min_qty.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Место хранения:").grid(row=2, column=2, padx=5, pady=5)
        self.entry_location = ttk.Entry(lbl_frame, width=20)
        self.entry_location.grid(row=2, column=3, padx=5, pady=5)

        btn_add = ttk.Button(lbl_frame, text="Добавить товар", command=self.add_product_action)
        btn_add.grid(row=2, column=4, columnspan=2, padx=10, pady=5)

        # Кнопки управления
        btn_frame = ttk.Frame(self.frame_products)
        btn_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(btn_frame, text="Обновить", command=self.refresh_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранный", command=self.delete_product_action).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Показать дефицит", command=self.show_low_stock).pack(side="left", padx=5)

        # Таблица товаров
        columns = ("ID", "Артикул", "Название", "Категория", "Ед.", "Кол-во кг", "Цена за кг", "Мин.ост.", "Место")
        self.tree_products = ttk.Treeview(self.frame_products, columns=columns, show="headings")
        for col in columns:
            self.tree_products.heading(col, text=col)
            self.tree_products.column(col, width=80)

        self.tree_products.column("Название", width=150)
        self.tree_products.column("Место", width=100)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.frame_products, orient="vertical", command=self.tree_products.yview)
        self.tree_products.configure(yscrollcommand=scrollbar.set)

        self.tree_products.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def setup_income_tab(self):
        lbl_frame = ttk.LabelFrame(self.frame_income, text="Оформление прихода товара")
        lbl_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(lbl_frame, text="ID Товара:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_income_product_id = ttk.Entry(lbl_frame, width=10)
        self.entry_income_product_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Количество:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_income_qty = ttk.Entry(lbl_frame, width=10)
        self.entry_income_qty.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Комментарий:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_income_comment = ttk.Entry(lbl_frame, width=30)
        self.entry_income_comment.grid(row=0, column=5, padx=5, pady=5)

        btn_income = ttk.Button(lbl_frame, text="Оформить приход", command=self.income_action)
        btn_income.grid(row=0, column=6, padx=10, pady=5)

        ttk.Label(self.frame_income, text="Совет: ID товара можно посмотреть во вкладке Каталог товаров",
                 foreground="blue").pack(padx=10, pady=5)

    def setup_expense_tab(self):
        lbl_frame = ttk.LabelFrame(self.frame_expense, text="Оформление расхода товара")
        lbl_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(lbl_frame, text="ID Товара:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_expense_product_id = ttk.Entry(lbl_frame, width=10)
        self.entry_expense_product_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Количество:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_expense_qty = ttk.Entry(lbl_frame, width=10)
        self.entry_expense_qty.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(lbl_frame, text="Комментарий:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_expense_comment = ttk.Entry(lbl_frame, width=30)
        self.entry_expense_comment.grid(row=0, column=5, padx=5, pady=5)

        btn_expense = ttk.Button(lbl_frame, text="Оформить расход", command=self.expense_action)
        btn_expense.grid(row=0, column=6, padx=10, pady=5)

    def setup_history_tab(self):
        btn_frame = ttk.Frame(self.frame_history)
        btn_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(btn_frame, text="Обновить историю", command=self.refresh_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Экспорт в консоль", command=self.export_history).pack(side="left", padx=5)

        columns = ("ID Оп.", "Артикул", "Название", "Тип", "Кол-во", "Дата", "Комментарий")
        self.tree_history = ttk.Treeview(self.frame_history, columns=columns, show="headings")
        for col in columns:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=100)

        self.tree_history.column("Название", width=150)
        self.tree_history.column("Комментарий", width=200)
        self.tree_history.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_reports_tab(self):
        lbl_frame = ttk.LabelFrame(self.frame_reports, text="Статистика склада")
        lbl_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.report_text = tk.Text(lbl_frame, height=20, width=80)
        self.report_text.pack(padx=10, pady=10, fill="both", expand=True)

        btn_frame = ttk.Frame(self.frame_reports)
        btn_frame.pack(padx=10, pady=5)

        ttk.Button(btn_frame, text="Сформировать отчет", command=self.generate_report).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить", command=lambda: self.report_text.delete(1.0, 'end')).pack(side="left", padx=5)

    # Логика

    def refresh_data(self):
        """Обновление всех таблиц"""
        # Очистка таблиц
        for item in self.tree_products.get_children():
            self.tree_products.delete(item)
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)

        # Загрузка товаров
        products = self.db.get_all_products()
        for product in products:
            self.tree_products.insert("", "end", values=product)

        # Загрузка истории
        operations = self.db.get_all_operations()
        for op in operations:
            self.tree_history.insert("", "end", values=op)

    def add_product_action(self):
        article = self.entry_article.get()
        name = self.entry_name.get()
        category = self.entry_category.get()
        unit = self.entry_unit.get()
        quantity = self.entry_quantity.get()
        price = self.entry_price.get()
        min_qty = self.entry_min_qty.get()
        location = self.entry_location.get()

        if article and name and quantity and price:
            if self.db.add_product(article, name, category, unit, int(quantity),
                                   float(price), int(min_qty), location):
                messagebox.showinfo("Успех", "Товар добавлен в каталог!")
                self.clear_product_fields()
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Товар с таким артикулом уже существует!")
        else:
            messagebox.showwarning("Внимание", "Заполните обязательные поля (Артикул, Название, Кол-во, Цена)!")

    def clear_product_fields(self):
        self.entry_article.delete(0, 'end')
        self.entry_name.delete(0, 'end')
        self.entry_category.delete(0, 'end')
        self.entry_quantity.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.entry_location.delete(0, 'end')

    def delete_product_action(self):
        selected = self.tree_products.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления!")
            return

        item_values = self.tree_products.item(selected)['values']
        product_id = item_values[0]
        product_name = item_values[2]

        if messagebox.askyesno("Подтверждение", f"Удалить товар [{product_name}]?"):
            self.db.delete_product(product_id)
            messagebox.showinfo("Успех", "Товар удален!")
            self.refresh_data()

    def show_low_stock(self):
        low_stock = self.db.get_low_stock_products()
        if low_stock:
            msg = "Товары с низким остатком:\n\n"
            for item in low_stock:
                msg += f"- {item[2]} (Арт: {item[1]}) - Остаток: {item[5]} {item[4]}\n"
            messagebox.showwarning("Внимание по остаткам", msg)
        else:
            messagebox.showinfo("OK", "Все товары в достаточном количестве!")

    def income_action(self):
        product_id = self.entry_income_product_id.get()
        quantity = self.entry_income_qty.get()
        comment = self.entry_income_comment.get()

        if product_id and quantity:
            product = self.db.get_product_by_id(int(product_id))
            if product:
                new_qty = product[5] + int(quantity)
                self.db.update_product_quantity(int(product_id), new_qty)
                self.db.add_operation(int(product_id), "ПРИХОД", int(quantity), comment)
                messagebox.showinfo("Успех", f"Приход оформлен! Новый остаток: {new_qty}")
                self.entry_income_qty.delete(0, 'end')
                self.entry_income_comment.delete(0, 'end')
                self.refresh_data()
            else:
                messagebox.showerror("Ошибка", "Товар с таким ID не найден!")
        else:
            messagebox.showwarning("Внимание", "Заполните ID товара и количество!")

    def expense_action(self):
        product_id = self.entry_expense_product_id.get()
        quantity = self.entry_expense_qty.get()
        comment = self.entry_expense_comment.get()

        if product_id and quantity:
            product = self.db.get_product_by_id(int(product_id))
            if product:
                if product[5] >= int(quantity):
                    new_qty = product[5] - int(quantity)
                    self.db.update_product_quantity(int(product_id), new_qty)
                    self.db.add_operation(int(product_id), "РАСХОД", int(quantity), comment)
                    messagebox.showinfo("Успех", f"Расход оформлен! Новый остаток: {new_qty}")
                    self.entry_expense_qty.delete(0, 'end')
                    self.entry_expense_comment.delete(0, 'end')
                    self.refresh_data()
                else:
                    messagebox.showerror("Ошибка",
                        f"Недостаточно товара! На складе: {product[5]} {product[4]}, запрошено: {quantity}")
            else:
                messagebox.showerror("Ошибка", "Товар с таким ID не найден!")
        else:
            messagebox.showwarning("Внимание", "Заполните ID товара и количество!")

    def export_history(self):
        operations = self.db.get_all_operations()
        print("\n" + "="*80)
        print("ИСТОРИЯ ОПЕРАЦИЙ СКЛАДА")
        print("="*80)
        for op in operations:
            print(f"ID: {op[0]} | {op[1]} | {op[2]} | {op[3]} | {op[4]} | {op[5]}")
        print("="*80 + "\n")
        messagebox.showinfo("Экспорт", "История операций выведена в консоль!")

    def generate_report(self):
        products = self.db.get_all_products()
        operations = self.db.get_all_operations()

        total_products = len(products)
        total_value = sum(p[5] * p[6] for p in products)  # quantity * price
        low_stock = len(self.db.get_low_stock_products())

        income_count = sum(1 for op in operations if op[3] == "ПРИХОД")
        expense_count = sum(1 for op in operations if op[3] == "РАСХОД")

        # Исправлено: используем ASCII символы вместо псевдографики
        report = f"""
================================================================================
                    ОТЧЕТ ПО СКЛАДУ
                  {datetime.now().strftime('%d.%m.%Y %H:%M')}
================================================================================
| ВСЕГО ТОВАРОВ В КАТАЛОГЕ: {total_products:<35} |
| ОБЩАЯ СТОИМОСТЬ СКЛАДА: {total_value:,.2f} руб.{'':20} |
| ТОВАРОВ С НИЗКИМ ОСТАТКОМ: {low_stock:<32} |
================================================================================
| ВСЕГО ОПЕРАЦИЙ ПРИХОДА: {income_count:<35} |
| ВСЕГО ОПЕРАЦИЙ РАСХОДА: {expense_count:<35} |
================================================================================
| ТОП-5 ТОВАРОВ ПО КОЛИЧЕСТВУ:                                 |
"""
        sorted_products = sorted(products, key=lambda x: x[5], reverse=True)[:5]
        for i, p in enumerate(sorted_products, 1):
            # Исправлено: обычные вертикальные черты
            report += f"|   {i}. {p[2]:<30} {p[5]:>5} {p[4]}|\n"

        report += """================================================================================
"""

        self.report_text.delete(1.0, 'end')
        self.report_text.insert('1.0', report)

    def on_close(self):
        self.db.close()
        self.root.destroy()

# ==========================================
# ЗАПУСК
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()