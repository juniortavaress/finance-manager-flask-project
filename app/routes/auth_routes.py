from flask import Blueprint, render_template, redirect, url_for, current_app, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegistrationForm
from app.models import User, Currency, UserCurrency
from app import bcrypt, database as db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/new_user", methods=["GET", "POST"])
@login_required
def forms():
    if request.method == "POST":
        selected_currencies = request.form.getlist("currency[]")

        print(selected_currencies)

        for code in selected_currencies:
            currency = Currency.query.filter_by(code=code).first()
            if currency:
                uc = UserCurrency(
                    user_id=current_user.id,
                    currency_id=currency.id
                )
                db.session.add(uc)

        db.session.commit()
        return redirect(url_for("user.user_homepage", user_id=current_user.id))

    return render_template("forms_new_user.html")


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('user.user_homepage', user_id=user.id)) 
            else:
                form.password.errors.append("Incorrect password")
                form.password.data = ""
        else:
            form.email.errors.append("Email not registered")
    return render_template("login_page.html", page="login", form=form)


@auth_bp.route("/create_account", methods=["GET", "POST"])
def create_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, password=password, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # return redirect(url_for("user.user_homepage", user_id=user.id))
        # return redirect(url_for("auth.forms"))
        return render_template("forms_new_user.html")
    else:
        if "email" in form.errors:
            form.name.data = ""
            form.email.data = "" 
            form.password.data = ""
            form.confirm_password.data = ""
        return render_template("login_page.html", page="create_account", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
