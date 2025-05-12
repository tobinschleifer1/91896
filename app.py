from flask import Flask, render_template, request, redirect, url_for, session, flash
from workout_tracker.database_models import db, User

def create_app():
    # Initialize the app
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'  # TODO: Replace in production

    # DB setup
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_tracker/91896.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with app
    db.init_app(app)

    # Define routes
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
