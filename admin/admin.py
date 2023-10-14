from flask import Blueprint, render_template, session, g


class Admin:
    def __init__(self, nav) -> None:
        nav = nav
        admin = Blueprint(
            "admin", __name__, template_folder="templates", static_folder="static"
        )
        db = None

        @admin.route(
            "/index"
        )  # можно указывать единый оброботчик для разных URL адресов
        @admin.route("/")
        def index():  # оброботчик
            if "admin" in session:
                return render_template(
                    "./index.html", nav=nav, title="Admin panel"
                )
            else:
                return render_template("page404.html", nav=nav), 404
            
        @admin.before_request
        def before_request():
            global db
            db = g.get('link_db')

        @admin.teardown_request()
        def teardown_request( request ):
            global db   
            db = None
            return request
        
