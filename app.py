from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/bridgehub'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bridgehub.db'
app.config['SECRET_KEY'] = 'secret'

login_manager = LoginManager(app)
db = SQLAlchemy(app)


@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, name, email, phone_number, password):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


# crud
@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('list.html', users=users)


@app.route('/user/<int:id>')
def user(id):
    try:
        user = User.query.get(id)
        return jsonify(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            # hash_password=user.password
        )
    except:
        return 'There was a problem fetching the user'


@app.route('/add_user', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            user = User(request.form['name'], request.form['email'],
                        request.form['phone_number'], request.form['password'])
            if user.name and user.email and user.password:
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('index'))
            return render_template('add.html')
        except:
            return 'There was a problem creating a new user'
    return render_template('add.html')


@app.route('/delete_user/<int:id>')
def delete(id):
    user = User.query.get(id)
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        return 'There was a problem deleting this user'
    return redirect(url_for('index'))


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = User.query.get(id)
    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            db.session.commit()
        except:
            return 'There was a problem editing user'
        return redirect(url_for('index'))
    return render_template('edit.html', user=user)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
