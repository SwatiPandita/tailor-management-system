from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            dress_type TEXT,
            chest REAL,
            waist REAL,
            shoulder REAL,
            sleeve REAL,
            length REAL,
            hip REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            garment TEXT,
            order_date TEXT,
            delivery_date TEXT,
            price REAL,
            advance REAL,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            amount REAL,
            payment_date TEXT,
            payment_method TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- DASHBOARD ----------------

@app.route("/")
def home():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        customer_count=customer_count,
        order_count=order_count
    )


# ---------------- ADD CUSTOMER ----------------

@app.route("/add-customer", methods=["GET", "POST"])
def add_customer():

    if request.method == "POST":

        name = request.form.get("name", "")
        phone = request.form.get("phone", "")
        email = request.form.get("email", "")
        address = request.form.get("address", "")

        conn = sqlite3.connect("tailor.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers
            (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (name, phone, email, address))

        conn.commit()
        conn.close()

        return redirect("/customers")

    return render_template("add_customer.html")


# ---------------- CUSTOMERS ----------------

@app.route("/customers")
def customers():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone, email, address
        FROM customers
        ORDER BY id DESC
    """)

    customer_list = cursor.fetchall()

    conn.close()

    return render_template(
        "customers.html",
        customers=customer_list
    )


# ---------------- MEASUREMENTS ----------------

@app.route("/measurements", methods=["GET", "POST"])
def measurements():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    if request.method == "POST":

        customer_name = request.form.get("customer_name", "")
        dress_type = request.form.get("dress_type", "")
        chest = request.form.get("chest", "")
        waist = request.form.get("waist", "")
        shoulder = request.form.get("shoulder", "")
        sleeve = request.form.get("sleeve", "")
        length = request.form.get("length", "")
        hip = request.form.get("hip", "")

        cursor.execute("""
            SELECT id FROM customers
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1
        """, (customer_name,))

        customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
        else:
            cursor.execute("""
                INSERT INTO customers
                (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            """, (customer_name, "", "", ""))

            customer_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO measurements
            (
                customer_id,
                dress_type,
                chest,
                waist,
                shoulder,
                sleeve,
                length,
                hip
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            dress_type,
            chest,
            waist,
            shoulder,
            sleeve,
            length,
            hip
        ))

        conn.commit()
        conn.close()

        return redirect("/measurements")

    cursor.execute("""
        SELECT id, name
        FROM customers
        ORDER BY name
    """)

    customer_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            measurements.id,
            customers.name,
            measurements.dress_type,
            measurements.chest,
            measurements.waist,
            measurements.shoulder,
            measurements.sleeve,
            measurements.length,
            measurements.hip
        FROM measurements
        JOIN customers
        ON measurements.customer_id = customers.id
        ORDER BY measurements.id DESC
    """)

    measurement_list = cursor.fetchall()

    conn.close()

    return render_template(
        "measurements.html",
        customers=customer_list,
        measurements=measurement_list
    )


# ---------------- ORDERS ----------------

@app.route("/orders", methods=["GET", "POST"])
def orders():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    if request.method == "POST":

        customer_name = request.form.get("customer_name", "")
        garment = request.form.get("garment", "")
        order_date = request.form.get("order_date", "")
        delivery_date = request.form.get("delivery_date", "")
        price = request.form.get("price", "")
        advance = request.form.get("advance", "")
        status = request.form.get("status", "Pending")

        cursor.execute("""
            SELECT id FROM customers
            WHERE LOWER(name) = LOWER(?)
            LIMIT 1
        """, (customer_name,))

        customer = cursor.fetchone()

        if customer:
            customer_id = customer[0]
        else:
            cursor.execute("""
                INSERT INTO customers
                (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            """, (customer_name, "", "", ""))

            customer_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO orders
            (
                customer_id,
                garment,
                order_date,
                delivery_date,
                price,
                advance,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            garment,
            order_date,
            delivery_date,
            price,
            advance,
            status
        ))

        conn.commit()
        conn.close()

        return redirect("/orders")

    cursor.execute("""
        SELECT id, name
        FROM customers
        ORDER BY name
    """)

    customer_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            orders.id,
            customers.name,
            orders.garment,
            orders.order_date,
            orders.delivery_date,
            orders.price,
            orders.advance,
            orders.status
        FROM orders
        JOIN customers
        ON orders.customer_id = customers.id
        ORDER BY orders.id DESC
    """)

    order_list = cursor.fetchall()

    conn.close()

    return render_template(
        "orders.html",
        customers=customer_list,
        orders=order_list
    )


# ---------------- PAYMENTS ----------------

@app.route("/payments", methods=["GET", "POST"])
def payments():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    if request.method == "POST":

        order_id = request.form.get("order_id")
        amount = request.form.get("amount")
        payment_date = request.form.get("payment_date")
        payment_method = request.form.get("payment_method")

        cursor.execute("""
            INSERT INTO payments
            (order_id, amount, payment_date, payment_method)
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            amount,
            payment_date,
            payment_method
        ))

        conn.commit()
        conn.close()

        return redirect("/payments")

    cursor.execute("""
        SELECT
            orders.id,
            customers.name,
            orders.garment,
            orders.price,
            orders.advance
        FROM orders
        JOIN customers
        ON orders.customer_id = customers.id
        ORDER BY orders.id DESC
    """)

    order_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            payments.id,
            customers.name,
            orders.garment,
            payments.amount,
            payments.payment_date,
            payments.payment_method
        FROM payments
        JOIN orders
        ON payments.order_id = orders.id
        JOIN customers
        ON orders.customer_id = customers.id
        ORDER BY payments.id DESC
    """)

    payment_list = cursor.fetchall()

    conn.close()

    return render_template(
        "payments.html",
        orders=order_list,
        payments=payment_list
    )


# ---------------- DELIVERIES ----------------

@app.route("/deliveries")
def deliveries():

    conn = sqlite3.connect("tailor.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            orders.id,
            customers.name,
            orders.garment,
            orders.order_date,
            orders.delivery_date,
            orders.status
        FROM orders
        JOIN customers
        ON orders.customer_id = customers.id
        ORDER BY orders.delivery_date ASC
    """)

    delivery_list = cursor.fetchall()

    conn.close()

    return render_template(
        "deliveries.html",
        deliveries=delivery_list
    )


# ---------------- START APP ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)