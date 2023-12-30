import sqlite3 as sq
import os
import io
from random import choice
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    session,
    redirect,
    g,
    send_file,
    make_response,
)
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from flask_socketio import SocketIO
from forms import *
from admin.admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


domen = "http://4-ch.online"

nav = [
    domen,
    {"name": "Flask", "url": "/index"},
    {"name": "About", "url": "/about"},
    {"name": "Feedback", "url": "/feedback"},
    {"name": "Login", "url": "/login"},
    {"name": "4chat", "url": "/4ch"},
]

gifarr = [
    "SteinsGate",
    "SteinsGatesad",
    "SteinsGatepsitiv",
    "eto-anime-girl",
    "Steins;Gateds2",
    "Steins;Gateds",
]

sk = "46205355d4292d929a7eb6313e47d468c3422df1"
DATABASE = "saper.db"
DEBUG = True
SECRET_KEY = f"{sk}"
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "saper.db")))
db_path = os.path.join(app.root_path, "saper.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

admin = Admin(nav)

app.register_blueprint(admin.admin, url_prefix="/admin")

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

db = SQLAlchemy(app)


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
    loggin = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    ava = db.Column(db.LargeBinary)


class Treds(db.Model):
    tred_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
    tred = db.Column(db.String(255), nullable=True)
    URL = db.Column(db.String(255), nullable=True, unique=True)
    img = db.Column(db.LargeBinary)


class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
    post = db.Column(db.String(255), nullable=True)
    img = db.Column(db.LargeBinary)
    tred_true = db.Column(db.String(255))
    type = db.Column(db.String(255))
    tred_name = db.Column(db.String(255), nullable=True)


# ======================== SOCKET ======================================
def video_socket(tred):
    """сокет для видео"""
    new_post = Posts.query.all()
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[-1].post_id}</span> Аноним:
                </div>
                <div class="post__content">
                    <video id="vid" onclick="videoOn('{new_post[-1].post_id}')" autoplay muted class="post_video" type="video/mp4" loop="1">
                        <source src="{ url_for('image_route', post_id=new_post[-1].post_id, tred=tred) }" type="video/mp4" />
                    </video>
                    <div id="video_play_{new_post[-1].post_id}" class="video_play_block video_play_block_new draggable">
                        <video id="video_{new_post[-1].post_id}" controls class="post_video video_play video_arr video_arr_new" type="video/mp4" loop="1">
                            <source src="{ url_for('image_route', post_id=new_post[-1].post_id, tred=tred) }" type="video/mp4" />
                        </video>
                    </div>
                    {new_post[-1].post}
                </div>
            </div>
        </div>
    """
    socketio.emit(tred, message)


def textmsg_socket(tred):
    """сокет для текстовых msg"""
    new_post = Posts.query.all()
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[-1].post_id}</span> Аноним:
                </div>
                <div class="post__content">
                    {new_post[-1].post}
                </div>
            </div>
        </div>
    """
    socketio.emit(tred, message)


def img_socket(tred):
    """сокет для картинок"""
    new_post = Posts.query.all()
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[-1].post_id}</span> Аноним:
                </div>
                <div class="post__content">
                    <a class="post-img-link" href="{ url_for('image_route', post_id=new_post[-1].post_id, tred=tred) }" target="_blank">
                        <img class="post_img" src="{ url_for('image_route', post_id=new_post[-1].post_id, tred=tred) }" alt="Image">
                    </a>
                    {new_post[-1].post}
                </div>
            </div>
        </div>
    """
    socketio.emit(tred, message)


# ======================== END SOCKET ======================================


@app.route("/index")
@app.route("/")
def index():
    """main page"""
    arr = Users.query.filter(Users.id_user == 1).all()
    return render_template("index.html", nav=nav, title="I love Flask!")


@app.route("/login", methods=["POST", "GET"])
def login():
    """залогинеться"""
    form = LoginForm()
    if request.cookies.get("logged"):
        log = request.cookies.get("logged")
        session["userLogged"] = log
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))
    elif form.validate_on_submit():
        if form.username.data == "admin" and form.psw.data == "admin" and 1 == 1:
            session["admin"] = True
            return redirect(url_for("admin.index"))
        users = Users.query.all()
        for i in range(len(users)):
            if (form.username.data == users[i].loggin) and check_password_hash(
                users[i].password, request.form["psw"]
            ):
                session["userLogged"] = form.username.data
                res = make_response(
                    redirect(url_for("profile", username=session["userLogged"]))
                )
                res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
                return res

    return render_template("login.html", nav=nav, title="Login", form=form)


@app.route("/logout")
def logout():
    """разлогинеться"""
    if "userLogged" in session:
        session.pop("userLogged")
    res = make_response(redirect(f"/profile/"))
    res.set_cookie("logged", "", 0)
    return res


@app.route("/4ch", methods=["POST", "GET"])
def tread():
    """постинг в 4ch"""
    if request.method == "POST":
        if request.files["image"]:
            filename = request.files["image"].filename
            if filename[-4:] == ".jpg" or filename[-4:] == ".png":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="jpeg",
                        tred_name="main",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                img_socket("posts")

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="mp4",
                        tred_name="main",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                video_socket("posts")

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="webm",
                        tred_name="main",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                video_socket("posts")

        else:
            try:
                addData = Posts(post=request.form["text-tread"], tred_name="main")
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()
            textmsg_socket("posts")

        return redirect(f"/4ch")
    else:
        gif = choice(gifarr)
        return render_template(
            "4ch.html",
            nav=nav,
            title="4ch",
            tred=Posts.query.filter(Posts.tred_name == "main").all(),
            gif=gif,
            tred_name="posts",
        )


@app.route("/image/<int:post_id>")
def image_route(post_id):
    """принимает запросы и выдаёт фотографии или фидео"""

    image_data = Posts.query.filter(Posts.post_id == post_id).all()
    if image_data:
        if image_data[0].type == "jpeg":
            file_type = "image"
        elif image_data[0].type == "mp4" or image_data[0].type == "webm":
            file_type = "video"
        return send_file(
            io.BytesIO(image_data[0].img), mimetype=f"{file_type}/{image_data[0].type}"
        )
    return "Image not found", 404


@app.route("/4ch/<tred_name>", methods=["POST", "GET"])
def tred(tred_name):
    """постинг в поддоменнах"""

    if request.method == "POST":
        if request.files["image"]:
            filename = request.files["image"].filename
            if filename[-4:] == ".jpg" or filename[-4:] == ".png":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="jpeg",
                        tred_name=tred_name,
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                img_socket(tred_name)

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="mp4",
                        tred_name=tred_name,
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                video_socket(tred_name)

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="webm",
                        tred_name=tred_name,
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                video_socket(tred_name)

        else:
            try:
                addData = Posts(post=request.form["text-tread"], tred_name=tred_name)
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()
            textmsg_socket(tred_name)

        return redirect(f"/4ch/{tred_name}")
    else:
        tred_title = tred_name.replace("_", " ")
        gif = choice(gifarr)

        return render_template(
            "tred.html",
            nav=nav,
            title=tred_title,
            tred_name=tred_name,
            tred=Posts.query.filter(Posts.tred_name == tred_name).all(),
            gif=gif,
        )


@app.route("/about")
def about():
    """пустая страница about"""
    return render_template("about.html", nav=nav, title="about Flask!")


@app.route("/tredcreate", methods=["POST", "GET"])
def tredcreate():
    """♥ работает ♥ Создане под доменов анологичных 4ch"""
    if request.method == "POST":
        if len(request.form["tred_name"]) > 2:
            tred_name = request.form["tred_name"]
            tred_nameURL = tred_name.replace(" ", "_")

            try:
                addData = Posts(
                    tred_true=f"/4ch/{tred_nameURL}", post=tred_name, tred_name="main"
                )
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()

    return redirect(f"/4ch")


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    """форма отцивов / неработает и не будет"""
    if request.method == "POST":
        if len(request.form["username"]) > 2:
            flash("Сообщение отправленно", category="success")
        else:
            flash("ошибка отправки", category="error")

    return render_template("feedback.html", nav=nav, title="Feedback")


@app.route("/profile/")
def profileLog():
    """левая ссылка для страцици 404 + проверяет куки"""
    if request.cookies.get("logged"):
        log = request.cookies.get("logged")
        session["userLogged"] = log
        return redirect(url_for("profile", username=log))
    else:
        return render_template("page404.html", nav=nav), 404


@app.route("/profile")
@app.route("/profile/<username>")
def profile(username):
    """профиль"""
    if "userLogged" not in session or session["userLogged"] != username:
        if request.cookies.get("logged"):
            log = request.cookies.get("logged")
            session["userLogged"] = log
            return redirect(url_for("profile", username=log))
        return redirect("/profile/")
    else:
        link = "/logout"
        return render_template("profile.html", nav=nav, title=username, link=link)


@app.route("/register", methods=["POST", "GET"])
def register():
    """регистрация пользователя"""
    users_reg = True
    form = RegisterForm()
    if form.validate_on_submit():
        users = Users.query.filter().all()
        for i in range(len(users)):
            if users[i].loggin == form.username.data:
                flash("этот loggin уже зянят", category="error")
                users_reg = False
                break
        if users_reg:
            hash = generate_password_hash(form.psw.data)
            if request.files["ava"]:
                img_file = request.files["ava"]
                img_binary = img_file.read()
                try:
                    addData = Users(
                        loggin=form.username.data, password=hash, ava=img_binary
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
            else:
                ava = None
                try:
                    addData = Users(loggin=form.username.data, password=hash, ava=ava)
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
            session["userLogged"] = form.username.data
            res = make_response(
                redirect(url_for("profile", username=session["userLogged"]))
            )
            res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
            return res
    return render_template("register.html", nav=nav, title="register", form=form)


@app.route("/profileImage/<loggin>")
def profileImage(loggin):
    """аватарка пользователя"""
    ava = Users.query.filter(Users.loggin == loggin).all()
    return send_file(io.BytesIO(ava[0].ava), mimetype="image/jpeg")


@app.errorhandler(404)
def pageNotFound(error):
    """странца 404"""
    return render_template("page404.html", nav=nav), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0")
