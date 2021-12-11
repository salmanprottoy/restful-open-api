import datetime
import json
from functools import wraps

import jwt
import mysql.connector
from flask import Flask, jsonify, request, make_response, redirect
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


# Token Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


# Unprotected Route and function
@app.route('/')
def index():
    return redirect('/login')


@app.route('/data', methods=['GET'])
def house():
    hotel_data = []

    db_connector = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="test"
    )

    title = request.args.get('title')
    bedroom = request.args.get('bedroom')
    sleep = request.args.get('sleeps')
    bathroom = request.args.get('bathroom')
    price = request.args.get('price')
    location = request.args.get('location')

    cursor = db_connector.cursor()
    # sleep  	bedroom  	bathroom  	price
    sql = "SELECT * FROM family_friendly_rentals WHERE "
    valudata = 0

    if (title != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Title LIKE " + f"'%{title}%'"
        else:
            sql = sql + "AND Title LIKE " + f"'%{title}%'"

    if (location != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Location LIKE " + f"'%{location}%'"
        else:
            sql = sql + "AND Location LIKE " + f"'%{location}%'"
    if (bedroom != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Bedroom LIKE " + f"'%{bedroom}%'"
        else:
            sql = sql + "AND Bedroom LIKE " + f"'%{bedroom}%'"
    if (bathroom != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Bathroom LIKE " + f"'%{bathroom}%'"
        else:
            sql = sql + "AND Bathroom LIKE" + f"'%{bathroom}%'"
    if (sleep != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Sleeps LIKE " + f"'%{sleep}%'"
        else:
            sql = sql + "AND Sleeps LIKE" + f"'%{sleep}%'"
    if (price != None):
        if (sql == 'SELECT * FROM family_friendly_rentals WHERE '):
            sql = sql + "Price LIKE" + f"'$%{price}%'"
        else:
            sql = sql + "AND Price LIKE " + f"'$%{price}%'"

    query = sql
    print(query)
    cursor.execute(query)

    results = cursor.fetchall()

    for x in results:
        data = {
            "id": x[0],
            "Title": x[1],
            "Location": x[2],
            "Sleeps": x[3],
            "Bedrooms": x[4],
            "Bathrooms": x[5],
            "Images": {
                "Image1": x[6][1:-1],
                "Image2": x[7][1:-1],
                "Image3": x[8][1:-1],
            },
            "Price": x[9],

        }
        hotel_data.append(data)
    hotel_data.sort(key=lambda x: x["Price"])
    houseJson = json.dumps(hotel_data, indent=4)
    print(houseJson)
    return houseJson


# Protected Route and function
@app.route('/protected')
@token_required
def protected():
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Restful OpenAPI"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    return redirect("/swagger", code=302)


# Login Route and function
@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == '1234':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=100)},
                           app.config['SECRET_KEY'])
        return jsonify(
            {'token': token, 'msg': 'use the token using token-url for accessing swagger',
             'token-url': f'/protected?token={token}'})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm:"Login Required"'})


if __name__ == "__main__":
    app.run(debug=False)
