from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegistrationForm
from app.models import User, Currency, UserCurrency
from app import database as db


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/new_user", methods=["GET", "POST"])
@login_required
def forms():
    """
    Manages the user onboarding process.
    
    GET: Renders the initial preference setup page (currency selection).
    POST: Processes and persists the user's selected currencies to the database.
    """
    if request.method == "POST":
        selected_currencies = request.form.getlist("currency[]")

        try:
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
        
        except:
            db.session.rollback()

    return render_template("forms_new_user.html")


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    """
    Authenticates the user and initiates the session.
    """
    if current_user.is_authenticated:
        return redirect(url_for('user.user_homepage', user_id=current_user.id))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(form.password.data):
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
    """
    Registers a new user and hashes the password using the model's logic.
    """
    if current_user.is_authenticated:
        return redirect(url_for('user.user_homepage', user_id=current_user.id))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(name=form.name.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
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
    """
    Ends the user session and redirects to the login page.
    """
    logout_user()
    return redirect(url_for("auth.login"))
