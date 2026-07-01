from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "mysecretkey"


def create_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            product TEXT,
            quantity INTEGER,
            price INTEGER,
            total INTEGER,
            name TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT,
            category TEXT
        )
    """)

    conn.commit()
    conn.close()


create_table()


@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))


@app.route("/products")
def products():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("products.html", products=products, user=session.get("user"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["price"] * item.get("quantity", 1) for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total, user=session.get("user"))


@app.route("/add-to-cart/<name>/<int:price>")
def add_to_cart(name, price):
    cart = session.get("cart", [])

    for item in cart:
        if item["name"] == name:
            item["quantity"] = item.get("quantity", 1) + 1
            session["cart"] = cart
            return redirect("/cart")

    cart.append({
        "name": name,
        "price": price,
        "quantity": 1
    })

    session["cart"] = cart
    return redirect("/cart")


@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    return redirect("/products")


@app.route("/remove-item/<name>")
def remove_item(name):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["name"] != name]
    session["cart"] = cart
    return redirect("/cart")


@app.route("/increase/<name>")
def increase(name):
    cart = session.get("cart", [])

    for item in cart:
        if item["name"] == name:
            item["quantity"] = item.get("quantity", 1) + 1

    session["cart"] = cart
    return redirect("/cart")


@app.route("/decrease/<name>")
def decrease(name):
    cart = session.get("cart", [])

    for item in cart:
        if item["name"] == name:
            item["quantity"] = item.get("quantity", 1) - 1
            if item["quantity"] < 1:
                item["quantity"] = 1

    session["cart"] = cart
    return redirect("/cart")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "<h1>Invalid Email or Password</h1>"

    return render_template("login.html", user=session.get("user"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return "<h2>Email already exists. Please use another email.</h2>"

    return render_template("signup.html", user=session.get("user"))


@app.route("/checkout")
def checkout():
    return render_template("checkout.html", user=session.get("user"))


@app.route("/place-order", methods=["POST"])
def place_order():
    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]
    city = request.form["city"]
    pincode = request.form["pincode"]

    cart = session.get("cart", [])

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    for item in cart:
        quantity = item.get("quantity", 1)

        cursor.execute("""
            INSERT INTO orders
            (user, product, quantity, price, total, name, phone, address, city, pincode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.get("user"),
            item["name"],
            quantity,
            item["price"],
            item["price"] * quantity,
            name,
            phone,
            address,
            city,
            pincode
        ))

    conn.commit()
    conn.close()

    session["cart"] = []

    return "<h1 style='text-align:center;'>🎉 Order Placed Successfully!</h1>"


@app.route("/my-orders")
def my_orders():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT product, quantity, price, total, name, phone, address, city, pincode FROM orders WHERE user=?",
        (session.get("user"),)
    )

    orders = cursor.fetchall()
    conn.close()

    return render_template("my_orders.html", orders=orders, user=session.get("user"))


@app.route("/admin")
def admin_dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT id, user, product, quantity, price, total, name, phone, address, city, pincode FROM orders")
    orders = cursor.fetchall()

    conn.close()

    return render_template("admin.html", users=users, orders=orders)


@app.route("/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        image = request.form["image"]
        category = request.form["category"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO products (name, price, image, category) VALUES (?, ?, ?, ?)",
            (name, price, image, category)
        )

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template("add_product.html", user=session.get("user"))


@app.route("/insert-products")
def insert_products():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    sample_products = [
        ("Laptop", 55000, "https://picsum.photos/200?random=1", "Electronics"),
        ("Mobile", 22000, "https://picsum.photos/200?random=2", "Electronics"),
        ("Headphones", 2500, "https://picsum.photos/200?random=3", "Accessories"),
        ("Watch", 3999, "https://picsum.photos/200?random=4", "Accessories")
    ]

    for product in sample_products:
        cursor.execute(
            "INSERT INTO products (name, price, image, category) VALUES (?, ?, ?, ?)",
            product
        )

    conn.commit()
    conn.close()

    return "Products Inserted Successfully"


@app.route("/check-orders")
def check_orders():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    conn.close()

    return str(orders)

@app.route("/clear-products")
def clear_products():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products")

    conn.commit()
    conn.close()

    return "Products Deleted"


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)