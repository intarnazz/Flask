from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Имя: ",
        validators=[
            DataRequired("без пробелов"),
            Length(min=4, max=100, message="минимум 3 символа"),
        ],
    )
    psw = PasswordField(
        "Пароль: ",
        validators=[
            DataRequired(),
            Length(min=3, max=100, message="минимум 3 символа"),
        ],
    )
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField(
        "Имя: ",
        validators=[
            DataRequired("без пробелов"),
            Length(min=4, max=100, message="минимум 3 символа"),
        ],
    )
    psw = PasswordField(
        "Пароль: ",
        validators=[
            DataRequired(),
            Length(min=3, max=100, message="минимум 3 символа"),
        ],
    )
    ava = FileField("Аватар: ")
    submit = SubmitField("Зарегистрироваться")
