from flask import Blueprint, render_template, session, g


class Admin:
    def __init__(self, nav) -> None:
        self.nav = nav
        self.admin = Blueprint(
            "admin", __name__, template_folder="templates", static_folder="static"
        )
        db = None

        @self.admin.route(
            "/index"
        )  # можно указывать единый оброботчик для разных URL адресов
        @self.admin.route("/")
        def index():  # оброботчик
            if "admin" in session:
                return render_template(
                    "./index.html", nav=self.nav, title="Admin panel"
                )
            else:
                return render_template("page404.html", nav=self.nav), 404
