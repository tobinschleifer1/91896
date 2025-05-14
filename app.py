from flask import Flask, render_template, request, redirect, url_for, session, flash
from workout_tracker.database_models import db, User

def create_app():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'  # TODO: Replace in production

    # DB setup
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_tracker/91896.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password')

        return render_template('login_page.html')

    @app.route('/home')
    def home():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('home_page.html')

    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            password_confirmation = request.form['password_confirmation']

            # Check if passwords match
            if password != password_confirmation:
                flash('Passwords do not match')
                return render_template('create_account.html')

            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
                return render_template('create_account.html')

            # Create new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully! You can now log in.')
            return redirect(url_for('login'))

        return render_template('create_account.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
