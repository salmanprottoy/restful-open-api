from flask import Flask, jsonify, request, make_response
import jwt
import datetime
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint

# from routes import request_api
app = Flask(__name__)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Flask Restful OpenAPI"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


# app.register_blueprint(request_api.get_blueprint())


app.config['SECRET_KEY'] = 'mysecretkey'


# Token Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


# Unprotected Route and function
@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Anyone can view this.'})


# Protected Route and function
@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'Only available to people with valid tokens.'})


# Login Route and function
@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == '1234':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=50)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm:"Login Required"'})


# @app.route('/static/<path:path>')
# def send_static(path):
#     return send_from_directory('static',path)
# app.register_blueprint(requset_api.get.get_blueprint())

if __name__ == "__main__":
    app.run(debug=True)
