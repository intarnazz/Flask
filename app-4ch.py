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
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send
from forms import *
from admin.admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

domen = "http://127.0.0.1:5000"

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
db_path = os.path.join(app.root_path, "saper.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
CORS(app)

admin = Admin(nav)

app.register_blueprint(admin.admin, url_prefix="/admin")

socketio = SocketIO(app, cors_allowed_origins="*")

db = SQLAlchemy(app)


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
    loggin = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    ava = db.Column(db.LargeBinary)
    header = db.Column(db.LargeBinary)


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
    like = db.Column(db.Integer)
    dislike = db.Column(db.Integer)
    autor = db.Column(db.String(255), nullable=True)


class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=True)
    post_id = db.Column(db.Integer, nullable=True)
    comment_text = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)


# def connect_db():
#     conn = sq.connect(app.config["DATABASE"])
#     # conn.row_factory = sq.Row
#     return conn
# def create_db():
#     """функция для создания таблиц бд"""
#     db = connect_db()
#     with app.open_resource("sq_db.sql", mode="r") as file:
#         db.cursor().executescript(file.read())
#     db.commit()
#     db.close()
# def get_db():
#     """соединение с бд"""
#     if not hasattr(g, "link_db"):
#         g.link_db = connect_db()
#     return g.link_db


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

# @app.teardown_appcontext
# def close_db(error):
#     """соединение с бд"""
#     if hasattr(g, "link_db"):
#         g.link_db.close()


@app.route("/index")  # можно указывать единый оброботчик для разных URL адресов
@app.route("/")
def index():  # оброботчик
    """main page"""
    arr = Users.query.filter(Users.id_user == 1).all()
    print(arr[0].loggin)
    return render_template("index.html", nav=nav, title="I love Flask!")


@app.route("/login", methods=["POST", "GET"])
def login():  # оброботчик
    """залогинеться"""
    form = LoginForm()
    if request.cookies.get("logged"):
        log = request.cookies.get("logged")
        session["userLogged"] = log
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))
    elif form.validate_on_submit():  # эквивалент  if request.method == "POST":
        if form.username.data == "admin" and form.psw.data == "admin" and 1 == 1:
            session["admin"] = True
            return redirect(url_for("admin.index"))
        users = Users.query.all()
        for i in range(len(users)):
            print(users)
            print(users[i].loggin)
            print(users[i].password)
            if (form.username.data == users[i].loggin) and check_password_hash(
                users[i].password, request.form["psw"]
            ):
                session["userLogged"] = form.username.data
                res = make_response(
                    redirect(url_for("profile", username=session["userLogged"]))
                )
                res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
                return res
    elif request.method == "POST":  # api
        data = request.get_json()
        users = Users.query.all()
        for i in range(len(users)):
            print(data["password"])
            if (data["login"] == users[i].loggin) and check_password_hash(
                users[i].password, data["password"]
            ):
                return jsonify({"code": 200})
        return jsonify({"code": 500})

    return render_template("login.html", nav=nav, title="Login", form=form)


@app.route("/logout")
def logout():  # оброботчик
    """разлогинеться"""
    if "userLogged" in session:
        session.pop("userLogged")
    res = make_response(redirect(f"/profile/"))
    res.set_cookie("logged", "", 0)
    return res


@app.route("/getVideo", methods=["POST", "GET"])
def getVideo():  # оброботчик
    """api"""
    arr = Posts.query.filter(Posts.tred_name == "video_api").all()
    res = {}
    for i in arr:
        res[i.post_id] = {
            "name": i.post,
        }
    return jsonify({"data": res})


@app.route("/getVideo/<autor>", methods=["POST", "GET"])
def getVideoAutor(autor):  # оброботчик
    """api"""
    arr = Posts.query.filter(Posts.tred_name == "video_api", Posts.autor == autor).all()
    res = {}
    for i in arr:
        res[i.post_id] = {
            "name": i.post,
        }
    return jsonify({"data": res})


@app.route("/api/Comment", methods=["POST", "GET"])
def apiComments():  # оброботчик
    """api"""
    if request.method == "POST":
        data = request.get_json()
        users = Users.query.all()
        for i in range(len(users)):
            if (data["login"] == users[i].loggin) and check_password_hash(
                users[i].password, data["password"]
            ):
                try:
                    addData = Comments(
                        post_id=data["post_id"],
                        comment_text=data["comment_text"],
                        user_id=Users.query.filter(Users.loggin == data["login"])
                        .all()[0]
                        .id_user,
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                    return jsonify({"code": 500})
                return jsonify({"code": 200})

    return jsonify({"code": 500})


@app.route("/api/GetComment/<int:post_id>", methods=["POST", "GET"])
def apiGetComments(post_id):  # оброботчик
    """api"""
    comments = Comments.query.filter(Comments.post_id == post_id).all()
    res = {}
    for i in range(len(comments)):
        res[i] = {
            "text": comments[i].comment_text,
            "user": Users.query.filter(Users.id_user == comments[i].user_id)
            .all()[0]
            .loggin,
        }
    return jsonify(res)


@app.route("/getVideo/<int:id>", methods=["POST", "GET"])
def apiGetID(id):  # оброботчик
    """api"""
    arr = Posts.query.filter(Posts.post_id == id).all()
    res = {}
    res[arr[0].post_id] = {
        "name": arr[0].post,
        "like": arr[0].like,
        "dislike": arr[0].dislike,
        "autor": arr[0].autor,
    }
    return jsonify({"data": res})


@app.route("/api/like/<int:id>", methods=["POST", "GET"])
def like(id):  # оброботчик
    """api"""
    delta = int(request.args.get("delta"))
    event = request.args.get("event")
    posts_item = Posts.query.get(id)
    if event == "like":
        if posts_item.like == None:
            posts_item.like = 0 + delta
        else:
            posts_item.like = int(posts_item.like) + delta
        db.session.commit()
        return jsonify({"like": posts_item.like})
    elif event == "dislike":
        if posts_item.dislike == None:
            posts_item.dislike = 0 + delta
        else:
            posts_item.dislike = int(posts_item.dislike) + delta
        db.session.commit()
        return jsonify({"like": posts_item.dislike})


@app.route("/4ch", methods=["POST", "GET"])
def tread():  # оброботчик
    """постинг в 4ch"""
    if request.method == "POST":
        if request.files["image"]:
            print(request.files["image"].filename)
            filename = request.files["image"].filename
            print(filename[-4:])
            if filename[-4:] == ".jpg" or filename[-4:] == ".png":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="jpeg",
                        tred_name="main",
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                img_socket("posts")

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="mp4",
                        tred_name="main",
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                video_socket("posts")

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="webm",
                        tred_name="main",
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                video_socket("posts")

        else:
            print("пост txt")
            try:
                addData = Posts(
                    post=request.form["text-tread"],
                    tred_name="main",
                    autor="root",
                )
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()
                print("ошибка чтения бд")
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
    # tred = request.args.get("tred")
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
def tred(tred_name):  # оброботчик
    """постинг в поддоменнах"""
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
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="jpeg",
                        tred_name=tred_name,
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                img_socket(tred_name)

            elif filename[-4:] == ".mp4":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="mp4",
                        tred_name=tred_name,
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                video_socket(tred_name)

            elif filename[-5:] == ".webm":
                img_file = request.files["image"]
                img_binary = img_file.read()
                print("пост картинки")
                try:
                    addData = Posts(
                        post=request.form["text-tread"],
                        img=img_binary,
                        type="webm",
                        tred_name=tred_name,
                        autor="root",
                    )
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
                video_socket(tred_name)

        else:
            print("пост txt")
            try:
                addData = Posts(
                    post=request.form["text-tread"],
                    tred_name=tred_name,
                    autor="root",
                )
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()
                print("ошибка чтения бд")
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
def about():  # оброботчик
    """пустая страница about"""
    return render_template("about.html", nav=nav, title="about Flask!")


@app.route("/tredcreate", methods=["POST", "GET"])
def tredcreate():  # оброботчик
    """♥ работает ♥ Создане под доменов анологичных 4ch"""
    if request.method == "POST":
        if len(request.form["tred_name"]) > 2:
            tred_name = request.form["tred_name"]
            print("tred_name", tred_name)
            tred_nameURL = tred_name.replace(" ", "_")

            try:
                addData = Posts(
                    tred_true=f"/4ch/{tred_nameURL}",
                    post=tred_name,
                    tred_name="main",
                    autor="root",
                )
                db.session.add(addData)
                db.session.flush()
                db.session.commit()
            except:
                db.session.rollback()
                print("ошибка чтения бд /tredcreate")

    return redirect(f"/4ch")


@app.route("/feedback", methods=["POST", "GET"])
def feedback():  # оброботчик
    """форма отцивов / неработает и не будет"""
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
    """левая ссылка для страцици 404 + проверяет куки"""
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
def register():  # оброботчик
    """регистрация пользователя"""
    users_reg = True
    form = RegisterForm()
    if form.validate_on_submit():
        users = Users.query.filter().all()
        for i in range(len(users)):
            if users[i].loggin == form.username.data:
                flash("этот loggin уже зянят", category="error")
                users_reg = False
                print("Логин занят")
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
                    print("ошибка чтения бд")
            else:
                ava = None
                try:
                    addData = Users(loggin=form.username.data, password=hash, ava=ava)
                    db.session.add(addData)
                    db.session.flush()
                    db.session.commit()
                except:
                    db.session.rollback()
                    print("ошибка чтения бд")
            session["userLogged"] = form.username.data
            res = make_response(
                redirect(url_for("profile", username=session["userLogged"]))
            )
            res.set_cookie("logged", form.username.data, 30 * 24 * 3600)
            return res
    return render_template("register.html", nav=nav, title="register", form=form)


@app.route("/profileImage/<loggin>")
def profileImage(loggin):  # оброботчик
    """аватарка пользователя"""
    user = Users.query.filter(Users.loggin == loggin).all()
    return send_file(io.BytesIO(user[0].ava), mimetype="image/jpeg")


@app.route("/profileHeader/<loggin>")
def profileHeader(loggin):  # оброботчик
    """шапка пользователя"""
    user = Users.query.filter(Users.loggin == loggin).all()
    if user[0].header == None:
        return send_file("./static/img/userHeaderDef.jpg", mimetype="image/jpeg")
    else:
        return send_file(io.BytesIO(user[0].header), mimetype="image/jpeg")


@app.route("/profileImageUpdade", methods=["POST", "GET"])
def profileImageUpdade():
    print("profileImageUpdade")
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        ava = request.files["ava"]
        user = Users.query.filter(Users.loggin == login).first()
        if user and check_password_hash(user.password, password):
            try:
                if ava.filename == "ava.jpg":
                    user.ava = ava.read()
                    print("ava")
                elif ava.filename == "header.jpg":
                    print("header")
                    user.header = ava.read()
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Ошибка при коммите в бд: {str(e)}")
                return jsonify({"code": 500, "error_message": str(e)})
            except Exception as e:
                db.session.rollback()
                print(f"Другая ошибка при коммите в бд: {str(e)}")
                return jsonify({"code": 500, "error_message": str(e)})

            return jsonify({"code": 200})
        return jsonify({"code": 500})


@app.route("/getUser/<login>")
def getUser(login):
    user = Users.query.filter(Users.loggin == login).first()
    try:
        return jsonify({"code": 200, "login": user.loggin})
    except AttributeError:
        return jsonify({"code": 500})


# ==== тестовый контекст запроса ====
# можно создовать в целях отдки оброботчиков
# with app.test_request_context():
#     print ( url_for('index') )
# ==// тестовый контекст запроса //==


@app.errorhandler(404)
def pageNotFound(error):
    """странца 404"""
    return render_template("page404.html", nav=nav), 404


# @app.before_request
# def before_request():
#     global data_base
#     db = get_db()
#     data_base = FDataBase(db)


# === запуск web-сервера ==
if __name__ == "__main__":
    app.run(debug=True)
# =// запуск web-сервера //=

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=80)
