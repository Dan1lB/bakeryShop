import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# Функція для підключення до бази даних
def connect_db():
    return psycopg2.connect(
        dbname="KR",
        user="danilbarabas",
        password="090105",
        host="localhost",
        port="5432"
    )

# Функція для виконання запиту до бази даних
def execute_query(query, params=(), fetch=False):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return result

# Основний клас програми
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управління продажами")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.user_role = tk.StringVar()
        self.user_login = tk.StringVar()
        self.user_password = tk.StringVar()

        tk.Label(self, text="Вибір ролі").pack(pady=5)
        tk.Radiobutton(self, text="Адміністратор", variable=self.user_role, value="admin").pack(pady=5)
        tk.Radiobutton(self, text="Клієнт", variable=self.user_role, value="client").pack(pady=5)

        tk.Label(self, text="Логін").pack(pady=5)
        tk.Entry(self, textvariable=self.user_login).pack(pady=5)

        tk.Label(self, text="Пароль").pack(pady=5)
        tk.Entry(self, textvariable=self.user_password, show="*").pack(pady=5)

        tk.Button(self, text="Увійти", command=self.login).pack(pady=20)

    def login(self):
        role = self.user_role.get()
        login = self.user_login.get()
        password = self.user_password.get()
        table = "administrators" if role == "admin" else "customers"
        
        user = execute_query(f"SELECT * FROM {table} WHERE login=%s AND password=%s", (login, password), fetch=True)

        if user:
            self.open_admin_interface() if role == "admin" else self.open_client_interface()
        else:
            messagebox.showerror("Помилка", "Неправильний логін або пароль")

    def open_admin_interface(self):
        self.destroy()
        AdminInterface()

    def open_client_interface(self):
        self.destroy()
        ClientInterface()

# Інтерфейс для клієнта
class ClientInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Інтерфейс клієнта")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="Додати замовлення", command=self.add_order).pack(pady=10)
        tk.Button(self, text="Переглянути замовлення", command=self.view_orders).pack(pady=10)
        tk.Button(self, text="Назад", command=self.back).pack(pady=10)

    def add_order(self):
        AddOrderWindow(self)

    def view_orders(self):
        ViewOrdersWindow(self)

    def back(self):
        self.destroy()
        Application()

# Інтерфейс для адміністратора
class AdminInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Інтерфейс адміністратора")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.create_admin_buttons()

    def create_admin_buttons(self):
        buttons = [
            ("Переглянути замовлення", self.view_orders),
            ("Переглянути продукти", self.view_products),
            ("Переглянути поставки", self.view_supplies),
            ("Додати клієнта", self.add_client),
            ("Додати поставку", self.add_supply),
            ("Переглянути клієнтів", self.view_customers)
        ]
        for text, command in buttons:
            tk.Button(self, text=text, command=command).pack(pady=10)

    def view_orders(self):
        ViewOrdersWindow(self)

    def view_products(self):
        ViewProductsWindow(self)

    def view_supplies(self):
        ViewSuppliesWindow(self)

    def add_client(self):
        AddClientWindow(self)

    def add_supply(self):
        AddSupplyWindow(self)

    def view_customers(self):
        ViewCustomersWindow(self)

    def back(self):
        self.destroy()
        Application()

# Вікно для додавання замовлення
class AddOrderWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Додати замовлення")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.product_id = tk.StringVar()
        self.quantity = tk.IntVar()
        self.delivery_date = tk.StringVar()

        tk.Label(self, text="Вибір продукту").pack(pady=5)
        product_menu = ttk.Combobox(self, textvariable=self.product_id)
        product_menu.pack(pady=5)
        self.load_products(product_menu)

        tk.Label(self, text="Кількість").pack(pady=5)
        tk.Entry(self, textvariable=self.quantity).pack(pady=5)

        tk.Label(self, text="Дата доставки").pack(pady=5)
        tk.Entry(self, textvariable=self.delivery_date).pack(pady=5)

        tk.Button(self, text="Зберегти замовлення", command=self.save_order).pack(pady=20)
        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

    def load_products(self, menu):
        products = execute_query("SELECT product_id, name FROM products", fetch=True)
        product_list = [f"{product[0]} - {product[1]}" for product in products]
        menu['values'] = product_list

    def save_order(self):
        product_id = self.product_id.get().split(" - ")[0]
        quantity = self.quantity.get()
        delivery_date = self.delivery_date.get()

        execute_query("INSERT INTO orders (product_id, quantity, order_date) VALUES (%s, %s, %s)",
                      (product_id, quantity, delivery_date))

        messagebox.showinfo("Успіх", "Замовлення збережено успішно")
        self.destroy()

# Вікно для перегляду замовлень
class ViewOrdersWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Переглянути замовлення")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("ID замовлення", "Товар", "Кількість", "Дата"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Видалити замовлення", command=self.delete_order).pack(pady=10)
        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

        self.load_orders()

    def load_orders(self):
        orders = execute_query("""
            SELECT o.order_id, p.name, o.quantity, o.order_date
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
        """, fetch=True)
        
        for order in orders:
            self.tree.insert("", tk.END, values=order)

    def delete_order(self):
        try:
            selected_item = self.tree.selection()[0]
            order_id = self.tree.item(selected_item)['values'][0]
            execute_query("DELETE FROM orders WHERE order_id=%s", (order_id,))
            self.tree.delete(selected_item)
            messagebox.showinfo("Успіх", "Замовлення видалено успішно")
        except IndexError:
            messagebox.showerror("Помилка", "Будь ласка, виберіть замовлення для видалення")

# Вікно для перегляду продуктів
class ViewProductsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Переглянути продукти")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("ID продукту", "Назва", "Ціна", "Дата"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

        self.load_products()

    def load_products(self):
        products = execute_query("SELECT * FROM products", fetch=True)
        for product in products:
            self.tree.insert("", tk.END, values=product)

# Вікно для перегляду поставок
class ViewSuppliesWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Переглянути поставки")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("ID поставки", "Продукт", "Дата", "Постачальник"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

        self.load_supplies()

    def load_supplies(self):
        supplies = execute_query("SELECT * FROM deliveries", fetch=True)
        for supply in supplies:
            self.tree.insert("", tk.END, values=supply)

# Вікно для додавання клієнта
class AddClientWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Додати клієнта")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        self.name = tk.StringVar()
        self.address = tk.StringVar()
        self.phone = tk.StringVar()
        self.login = tk.StringVar()
        self.password = tk.StringVar()

        tk.Label(self, text="Ім'я").pack(pady=5)
        tk.Entry(self, textvariable=self.name).pack(pady=5)

        tk.Label(self, text="Адреса").pack(pady=5)
        tk.Entry(self, textvariable=self.address).pack(pady=5)

        tk.Label(self, text="Телефон").pack(pady=5)
        tk.Entry(self, textvariable=self.phone).pack(pady=5)

        tk.Label(self, text="Логін").pack(pady=5)
        tk.Entry(self, textvariable=self.login).pack(pady=5)

        tk.Label(self, text="Пароль").pack(pady=5)
        tk.Entry(self, textvariable=self.password, show="*").pack(pady=5)

        tk.Button(self, text="Зберегти клієнта", command=self.save_client).pack(pady=20)
        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

    def save_client(self):
        name = self.name.get()
        address = self.address.get()
        phone = self.phone.get()
        login = self.login.get()
        password = self.password.get()

        execute_query("INSERT INTO customers (name, address, phone, login, password) VALUES (%s, %s, %s, %s, %s)",
                      (name, address, phone, login, password))

        messagebox.showinfo("Успіх", "Клієнта додано успішно")
        self.destroy()

# Вікно для перегляду клієнтів
class ViewCustomersWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Переглянути клієнтів")
        self.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("ID клієнта", "Ім'я", "Адреса", "Телефон", "Логін"), show='headings')
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Назад", command=self.destroy).pack(pady=10)

        self.load_customers()

    def load_customers(self):
        customers = execute_query("SELECT customer_id, name, address, phone, login FROM customers", fetch=True)
        for customer in customers:
            self.tree.insert("", tk.END, values=customer)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
