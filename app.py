from flask import Flask, render_template, request, session, redirect, url_for
from cs50 import SQL
import os
import openai
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import base64
from functools import wraps
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.code = os.getenv("TEACHER_PASSWORD")
app.permanent_session_lifetime = timedelta(days=7)

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

db = SQL("sqlite:///items.db")

UPLOAD_FOLDER = "static/uploads"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    items = db.execute("SELECT * FROM items WHERE claimed = 0")
    return render_template("list_items.html", items=items)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("code")
        if code == app.code:
            session["logged_in"] = True
            session.permanent = True
            return redirect(url_for("index"))
        else:
            return "WRONG CODE", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/search")
def search():
    query = request.args.get("q")
    if query:
        items = db.execute("SELECT * FROM items WHERE claimed = 0 AND tags LIKE ?", f"%{query}%")
    else:
        items = db.execute("SELECT * FROM items WHERE claimed = 0")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("items_partial.html", items=items)
    return render_template("list_items.html", items=items)

@app.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        photo = request.files.get("photo")
        if not photo:
            return "Please Upload A File", 400
        filename = secure_filename(photo.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
        photo.save(filepath)
        with open(filepath, "rb") as file:
            b64_image = base64.b64encode(file.read()).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Give 3 short, space-separated capitalized tags describing this image. EX. Blue Nike Bottle MAKE SURE IT IS COLOR AND THE ACTUAL OBJECT, AND THEN THE LOGO IF THERE IS ANY. IF NO LOGO DETECTED LEAVE IT BLANK. E.G. Blue Bottle NO SPACES"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )
        responsetitle = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Give me a title. EX. Blue Nike Bottle. IF NO LOGO DETECTED LEAVE IT BLANK. E.G. Blue Bottle"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )
        title = responsetitle.choices[0].message.content
        tags = response.choices[0].message.content
        db.execute("INSERT INTO items (tags, image_path, title) VALUES (?, ?, ?)", tags, f"uploads/{filename}", title)
        return f"""
            <h2>Uploaded</h2>
            <img src="/static/uploads/{filename}" width="300"><br><br>
            <b>Tags:</b> {tags}
            <br><br><a href="/upload">Upload another</a><br><br>
            """
    else:
        return render_template("add.html")

@app.route("/claim")
@login_required
def claim_view():
    items = db.execute("SELECT * FROM items WHERE claimed = 0")
    return render_template("delete.html", items=items)

@app.route("/claim/<int:item_id>", methods=["POST"])
@login_required
def claim_item(item_id):
    name = request.form.get("claimer")
    db.execute("UPDATE items SET claimed = 1, claimed_by = ? WHERE id = ?", name, item_id)
    return redirect(url_for("claim_view"))

@app.route("/viewclaimed")
@login_required
def view_claimed():
    items = db.execute("SELECT * FROM items WHERE claimed = 1")
    return render_template("claimview.html", items=items)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)