from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = "bike_race_secret"

# MySQL Config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "bike_race_db"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

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


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_data = {
            "full_name": request.form["full_name"].strip(),
            "age": request.form["age"].strip(),
            "category": request.form["category"],
            "email": request.form["email"].strip().lower()
        }

        errors = validate_form(form_data)

        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("register"))

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO participants (full_name, age, category, email) VALUES (%s,%s,%s,%s)",
                (form_data["full_name"], form_data["age"], form_data["category"], form_data["email"])
            )
            mysql.connection.commit()
            cur.close()
            flash("Registration successful!", "success")

        except Exception as e:
            flash("Email already registered OR database error.", "danger")
            print("DB ERROR:", e)

        return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/participants")
def participants():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM participants ORDER BY id DESC")
        data = cur.fetchall()
        cur.close()
        return render_template("participants.html", participants=data)

    except Exception as e:
        print("FETCH ERROR:", e)
        return "Database error. Check your terminal."


if __name__ == "__main__":
    app.run(debug=True)
