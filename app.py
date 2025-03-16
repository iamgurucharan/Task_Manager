from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

# Define Database Credentials
user = 'root'
password = 'Gc%4019102006'  # URL-encoded password
host = '127.0.0.1'
port = 3306
database = 'task'

# Create Engine and Session
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base for ORM
Base = declarative_base()

# Task Model
class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)

# Create Database Tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Home Route - Show all Tasks
@app.route("/")
def index():
    tasks = db_session.query(Task).all()
    return render_template("index.html", tasks=tasks)

# Add Task Route
@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    if title:
        new_task = Task(title=title)
        try:
            db_session.add(new_task)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error: {e}")
    return redirect(url_for("index"))

# Mark Task as Completed
@app.route("/completed/<int:task_id>")
def complete_task(task_id):
    task = db_session.query(Task).get(task_id)
    if task:
        task.completed = not task.completed
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error: {e}")
    return redirect(url_for("index"))

# Delete Task Route
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = db_session.query(Task).get(task_id)
    if task:
        try:
            db_session.delete(task)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error: {e}")
    return redirect(url_for("index"))

# Close Database Session After Each Request
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Main Function
if __name__ == "__main__":
    # Create Database Tables
    create_tables()
    # Run Flask App
    app.run(debug=True)