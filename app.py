from flask import Flask
from flask_jwt_extended import JWTManager
from controller.user_controller import user_bp
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
jwt = JWTManager(app)

app.register_blueprint(user_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=False)