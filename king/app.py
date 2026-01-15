from flask import Flask, request, redirect, url_for, flash, get_flashed_messages
from flask_mysqldb import MySQL
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = "bike_race_secret"

app.config.update(
    MYSQL_HOST="localhost",
    MYSQL_USER="root",
    MYSQL_PASSWORD="",
    MYSQL_DB="bike_race_db"
)

mysql = MySQL(app)


def validate_form(data):
    errors = []

    if not data["full_name"]:
        errors.append("Full name is required.")

    try:
        age = int(data["age"])
        if age < 10 or age > 100:
            errors.append("Age must be between 10 and 100.")
    except:
        errors.append("Age must be a number.")

    if data["category"] not in ["Beginner", "Intermediate", "Pro"]:
        errors.append("Invalid category selected.")

    try:
        validate_email(data["email"])
    except EmailNotValidError:
        errors.append("Invalid email address.")

    return errors


def render_page():
    messages = get_flashed_messages(with_categories=True)

    alerts = ""
    for category, msg in messages:
        alerts += f"<p style='color:red'>{msg}</p>" if category == "danger" else f"<p style='color:green'>{msg}</p>"

    return f"""
    <html>
    <head><title>Bike Race Registration</title></head>
    <body style="font-family: Arial">
        <h2>Bike Race Registration</h2>
        {alerts}

        <form method="POST">
            Full Name:<br>
            <input name="full_name"><br><br>

            Age:<br>
            <input name="age" type="number"><br><br>

            Category:<br>
            <select name="category">
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Pro</option>
            </select><br><br>

            Email:<br>
            <input name="email"><br><br>

            <button type="submit">Register</button>
        </form>

        <br>
        <a href="/participants">View Participants</a>
    </body>
    </html>
    """


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = {
            "full_name": request.form.get("full_name", "").strip(),
            "age": request.form.get("age", "").strip(),
            "category": request.form.get("category", ""),
            "email": request.form.get("email", "").strip().lower()
        }

        errors = validate_form(form_data)

        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("register"))

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO participants (full_name, age, category, email) VALUES (%s,%s,%s,%s)",
                (form_data["full_name"], form_data["age"], form_data["category"], form_data["email"])
            )
            mysql.connection.commit()
            flash("Registration Successful!", "success")

        except Exception as e:
            flash(str(e), "danger")

        finally:
            cur.close()

        return redirect(url_for("register"))

    return render_page()


@app.route("/participants")
def participants():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM participants ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()

    table = ""
    for r in rows:
        table += f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"

    return f"""
    <html>
    <head><title>Participants</title></head>
    <body style="font-family: Arial">
        <h2>Participants</h2>

        <table border="1" cellpadding="5">
            <tr>
                <th>Name</th><th>Age</th><th>Category</th><th>Email</th>
            </tr>
            {table}
        </table>

        <br>
        <a href="/">Back</a>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
