from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 從環境變數獲取 PostgreSQL 連線資訊
db_user = os.getenv("POSTGRESQL_USER", "postgres")
db_password = os.getenv("POSTGRESQL_PASSWORD", "password")
db_host = os.getenv("POSTGRES_HOST", "postgres-service")
db_name = os.getenv("POSTGRESQL_DATABASE", "todo_db")

# 配置 SQLAlchemy 的資料庫 URI
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 定義 TODO 模型
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# 創建資料表
with app.app_context():
    db.create_all()

# 網頁路由：首頁，顯示所有 TODO 項目
@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)

# 網頁路由：新增 TODO 頁面
@app.route("/add", methods=["GET", "POST"])
def add_todo_web():
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            todo = Todo(task=task, completed=False)
            db.session.add(todo)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("add_todo.html", error="Task is required")
    return render_template("add_todo.html")

# 網頁路由：刪除 TODO
@app.route("/delete/<int:id>", methods=["POST"])
def delete_todo_web(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))

# 網頁路由：切換完成狀態
@app.route("/toggle/<int:id>", methods=["POST"])
def toggle_todo(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("index"))

# API 路由：獲取所有 TODO
@app.route("/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    return jsonify([{"id": t.id, "task": t.task, "completed": t.completed} for t in todos])

# API 路由：新增 TODO
@app.route("/todos", methods=["POST"])
def add_todo_api():
    data = request.get_json()
    if not data or not data.get("task"):
        return jsonify({"error": "Task is required"}), 400
    todo = Todo(task=data["task"], completed=False)
    db.session.add(todo)
    db.session.commit()
    return jsonify({"id": todo.id, "task": todo.task, "completed": todo.completed}), 201

# API 路由：更新 TODO
@app.route("/todos/<int:id>", methods=["PUT"])
def update_todo_api(id):
    todo = Todo.query.get_or_404(id)
    data = request.get_json()
    if data.get("task"):
        todo.task = data["task"]
    if "completed" in data:
        todo.completed = data["completed"]
    db.session.commit()
    return jsonify({"id": todo.id, "task": todo.task, "completed": todo.completed})

# API 路由：刪除 TODO
@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo_api(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)