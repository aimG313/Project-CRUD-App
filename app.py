import os
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
Scss(app)

# Use a writable /tmp directory for the SQLite database on Vercel
if os.environ.get("VERCEL"):
    db_path = "/tmp/database.db"
else:
    db_path = "database.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Mytask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"Task {self.id}"

with app.app_context():
    db.create_all()

# Homepage: Display and add tasks
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        # Trim whitespace and prevent empty inputs
        current_task = request.form["content"].strip()
        if not current_task:
            return "Empty input isn't accepted"
        new_task = Mytask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
    else:
        tasks = Mytask.query.order_by(Mytask.created).all()
        return render_template("task.html", tasks=tasks)

# Delete a task
@app.route("/delete/<int:id>")
def delete(id: int):
    delete_task = Mytask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"Error: {e}"

# Edit a task
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id: int):
    task = Mytask.query.get_or_404(id)
    if request.method == "POST":
        new_content = request.form["content"].strip()
        if not new_content:
            return "Empty input isn't accepted"
        task.content = new_content
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
    else:
        return render_template("edit.html", task=task)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)
