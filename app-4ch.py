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


domen = "http://127.0.0.1:5000/"

nav = [
    domen,
    {"name": "Flask", "url": "/index"},
    {"name": "About", "url": "/about"},
    {"name": "Feedback", "url": "/feedback"},
    {"name": "Login", "url": "/login"},
    {"name": "4chat", "url": "/4ch"},
]

# ==================================
#    session.modified = True
#  нужно прописывать в случае когда нам нужно изменить данные сессии,
#  обычно используется для увеличение числовых значений в сессии
#
#
# ==================================
# ==================================
#   session.permanent = True
#  Можно явно указать время жизни сессии:
#  app.permanent_session_lifetime = datetime.timedelta( days=10 )
#
#
# ==================================


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
socketio = SocketIO(app)


def connect_bd():
    conn = sq.connect(app.config["DATABASE"])
    # conn.row_factory = sq.Row
    return conn


def create_db():
    """функция для создания таблиц бд"""
    db = connect_bd()
    with app.open_resource("sq_db.sql", mode="r") as file:
        db.cursor().executescript(file.read())
    db.commit()
    db.close()


def get_db():
    """соединение с бд"""
    if not hasattr(g, "link_db"):
        g.link_db = connect_bd()
    return g.link_db


# ======================== SOCKET ======================================
def video_socket(tred):
    new_post = data_base.getEndTred(tred)
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[0][0]}</span> Аноним:
                </div>
                <div class="post__content">
                    <video id="vid" onclick="videoOn('{new_post[0][0]}')" autoplay muted class="post_video" type="video/mp4" loop="1">
                        <source src="{ url_for('image_route', post_id=new_post[0][0], tred=tred) }" type="video/mp4" />
                    </video>
                    <div id="video_play_{new_post[0][0]}" class="video_play_block video_play_block_new draggable">
                        <video id="video_{new_post[0][0]}" controls class="post_video video_play video_arr video_arr_new" type="video/mp4" loop="1">
                            <source src="{ url_for('image_route', post_id=new_post[0][0], tred=tred) }" type="video/mp4" />
                        </video>
                    </div>
                    {new_post[0][1]}
                </div>
            </div>
        </div>
    """
    socketio.emit("message", message)


def textmsg_socket(tred):
    new_post = data_base.getEndTred(tred)
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[0][0]}</span> Аноним:
                </div>
                <div class="post__content">
                    {new_post[0][1]}
                </div>
            </div>
        </div>
    """
    socketio.emit("message", message)


def img_socket(tred):
    new_post = data_base.getEndTred(tred)
    message = f"""
        <div class="out_post">
            <div class="boc">
                ...
            </div>
            <div class="post">
                <div class="annon-info">
                    <span class="post__id">{new_post[0][0]}</span> Аноним:
                </div>
                <div class="post__content">
                    <a class="post-img-link" href="{ url_for('image_route', post_id=new_post[0][0], tred=tred) }" target="_blank">
                        <img class="post_img" src="{ url_for('image_route', post_id=new_post[0][0], tred=tred) }" alt="Image">
                    </a>
                    {new_post[0][1]}
                </div>
            </div>
        </div>
    """
    socketio.emit("message", message)


# ======================== END SOCKET ======================================


@app.teardown_appcontext
def close_db(error):
    """соединение с бд"""
    if hasattr(g, "link_db"):
        g.link_db.close()


@app.route("/index")  # можно указывать единый оброботчик для разных URL адресов
@app.route("/")
def index():  # оброботчик
    return render_template("index.html", nav=nav, title="I love Flask!")


@app.route("/login", methods=["POST", "GET"])
def login():  # оброботчик
    form = LoginForm()
    if request.cookies.get("logged"):
        log = request.cookies.get("logged")
        session["userLogged"] = log
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))
    elif form.validate_on_submit():  # эквивалент  if request.method == "POST":
        users = data_base.getUsers()
        for i in range(len(users)):
            print(users[i][0])
            print(users[i][1])
            if (form.username.data == users[i][0]) and check_password_hash(
                users[i][1], request.form["psw"]
            ):
                session["userLogged"] = form.username.data
                res = make_response(
                    redirect(url_for("profile", username=session["userLogged"]))
                )
                res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
                return res

    return render_template("login.html", nav=nav, title="Login", form=form)


@app.route("/logout")
def logout():  # оброботчик
    if "userLogged" in session:
        session.pop("userLogged")
    res = make_response(redirect(f"/profile/"))
    res.set_cookie("logged", "", 0)
    return res


@app.route("/4ch", methods=["POST", "GET"])
def tread():  # оброботчик
    if request.method == "POST":
        if request.files["image"]:
            print(request.files["image"].filename)
            filename = request.files["image"].filename
            print(filename[-4:])
            if filename[-4:] == ".jpg" or filename[-4:] == ".png":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostImage(
                    request.form["text-tread"],
                    img_binary,
                    "jpeg",
                )
                img_socket("posts")

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostImage(
                    request.form["text-tread"],
                    img_binary,
                    "mp4",
                )
                video_socket("posts")

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostImage(
                    request.form["text-tread"],
                    img_binary,
                    "webm",
                )
                video_socket("posts")

        else:
            print("пост txt")
            resuld = data_base.addPost("posts", request.form["text-tread"])
            textmsg_socket("posts")

        return redirect(f"/4ch")
    else:
        gif = choice(gifarr)
        return render_template(
            "4ch.html",
            nav=nav,
            title="4ch",
            tred=data_base.getTred("posts"),
            gif=gif,
        )


@app.route("/image/<int:post_id>")
def image_route(post_id):
    tred = request.args.get("tred")
    image_data = data_base.get_image(post_id, tred)
    print(image_data[1])
    if image_data:
        if image_data[1] == "jpeg":
            file_type = "image"
        elif image_data[1] == "mp4" or image_data[1] == "webm":
            file_type = "video"
        return send_file(
            io.BytesIO(image_data[0]), mimetype=f"{file_type}/{image_data[1]}"
        )
    return "Image not found", 404


@app.route("/4ch/<tred_name>", methods=["POST", "GET"])
def tred(tred_name):  # оброботчик
    #
    #
    # if request.method == 'POST':

    #     img_file = request.files['image']
    #     img_binary = img_file.read()
    #     data_base.addPostPost( tred_name, request.form['text-tread'], img_binary )

    # tred_title = data_base.get_tred_name( f"/4ch/{tred_name}" )
    # print(tred_title)
    # tred_title = tred_title[0][0]
    # tred_title = tred_title.replace( "_", " " )

    # return render_template(
    #     'tred.html',
    #     nav=nav,
    #     title=tred_title,
    #     tred_name=tred_name,
    #     tred = data_base.getSubTred(tred_name), )

    if request.method == "POST":
        if request.files["image"]:
            print(request.files["image"].filename)
            filename = request.files["image"].filename
            print(filename[-4:])
            if filename[-4:] == ".jpg" or filename[-4:] == ".png":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostPost(
                    tred_name,
                    request.form["text-tread"],
                    img_binary,
                    "jpeg",
                )
                img_socket(tred_name)

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostPost(
                    tred_name,
                    request.form["text-tread"],
                    img_binary,
                    "mp4",
                )
                video_socket(tred_name)

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                resuld = data_base.addPostPost(
                    tred_name,
                    request.form["text-tread"],
                    img_binary,
                    "webm",
                )
                video_socket(tred_name)

        else:
            print("пост txt")
            resuld = data_base.addPost(tred_name, request.form["text-tread"])
            textmsg_socket(tred_name)

        return redirect(f"/4ch/{tred_name}")
    else:
        tred_title = data_base.get_tred_name(f"/4ch/{tred_name}")
        print(tred_title)
        tred_title = tred_title[0][0]
        tred_title = tred_title.replace("_", " ")
        gif = choice(gifarr)

        return render_template(
            "tred.html",
            nav=nav,
            title=tred_title,
            tred_name=tred_name,
            tred=data_base.getSubTred(tred_name),
            gif=gif,
        )


@app.route("/about")
def about():  # оброботчик
    return render_template("about.html", nav=nav, title="about Flask!")


@app.route("/tredcreate", methods=["POST", "GET"])
def tredcreate():  # оброботчик
    if request.method == "POST":
        if len(request.form["tred_name"]) > 2:
            tred_name = request.form["tred_name"]
            print("tred_name", tred_name)
            tred_name = tred_name.replace(" ", "_")

            data_base.create_trad(tred_name)
            tred = data_base.get_id_url()
            # link = domen, str(tred[0][1]), str(tred[0][0])
            # print(link)
            data_base.addTred(f"/4ch/{tred[0][1]}{tred[0][0]}", tred_name, tred[0][0])

    return redirect(f"/4ch")


@app.route("/feedback", methods=["POST", "GET"])
def feedback():  # оброботчик
    if request.method == "POST":
        # print(request.form)
        # print(request.form['username'])
        if len(request.form["username"]) > 2:
            flash("Сообщение отправленно", category="success")
        else:
            flash("ошибка отправки", category="error")

    return render_template("feedback.html", nav=nav, title="Feedback")


# @app.route("/profile/<int:username>")   - только цифры
# @app.route("/profile/<float:username>") - число с плавующей точкой
# @app.route("/profile/<path:username>")  - url-адрес
@app.route("/profile/")
def profileLog():  # оброботчик
    print("profile")
    if request.cookies.get("logged"):
        print("чтетие куки")
        log = request.cookies.get("logged")
        session["userLogged"] = log
        return redirect(url_for("profile", username=log))
    else:
        return render_template("page404.html", nav=nav), 404


@app.route("/profile")
@app.route("/profile/<username>")
def profile(username):  # оброботчик
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
def register():  # оброботчик
    users_reg = True
    form = RegisterForm()
    if form.validate_on_submit():
        users = data_base.getUsers()
        for i in range(len(users)):
            if users[i][0] == form.username.data:
                flash("этот loggin уже зянят", category="error")
                users_reg = False
                print("Логин занят")
                break
        if users_reg:
            hash = generate_password_hash(form.psw.data)
            if request.files["ava"]:
                img_file = request.files["ava"]
                img_binary = img_file.read()
                data_base.addUser(form.username.data, hash, img_binary)
            else:
                ava = None
                data_base.addUser(form.username.data, hash, ava)
            session["userLogged"] = form.username.data
            res = make_response(
                redirect(url_for("profile", username=session["userLogged"]))
            )
            res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
            return res
    return render_template("register.html", nav=nav, title="register", form=form)


@app.route("/profileImage/<loggin>")
def profileImage(loggin):  # оброботчик
    ava = data_base.getUserAva(loggin)
    return send_file(io.BytesIO(ava[0][0]), mimetype="image/jpeg")


# ==== тестовый контекст запроса ====
# можно создовать в целях отдки оброботчиков
# with app.test_request_context():
#     print ( url_for('index') )
# ==// тестовый контекст запроса //==


@app.errorhandler(404)
def pageNotFound(error):
    return render_template("page404.html", nav=nav), 404


@app.before_request
def before_request():
    global data_base
    db = get_db()
    data_base = FDataBase(db)


# === запуск web-сервера ==
if __name__ == "__main__":
    app.run(debug=True)
# =// запуск web-сервера //=


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80)
