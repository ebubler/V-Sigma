from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from flask_wtf.file import FileAllowed

class AddPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    file = FileField('Файл', validators=[Optional()])
    content = FileField('Контент', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'],'Только изображения!')])
    submit = SubmitField('Добавить пост')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class Edit_prof(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    photo_avatar = FileField(
        'Загрузить аватар',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')]
    )
    photo_banner = FileField(
        'Загрузить баннер',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')]
    )
    submit = SubmitField('Сохранить изменения')