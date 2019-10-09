from flask import (Flask, render_template, request, session,
                   Response, jsonify)
from database import connector
from model import entities
import datetime
import json

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/message-table', methods=['GET'])
def message_table():
    sessionc = db.getSession(engine)
    raw_messages = sessionc.query(entities.Message)
    raw_messages = raw_messages[:]
    messages = json.dumps(raw_messages, cls=connector.AlchemyEncoder)
    return render_template('chat.html', messages=json.loads(messages))


@app.route('/user-table', methods=['GET'])
def user_table():
    session = db.getSession(engine)
    raw_users = session.query(entities.User)
    raw_users = raw_users[:]
    users = json.dumps(raw_users, cls=connector.AlchemyEncoder)
    return render_template('users.html', users=json.loads(users))


@app.route('/conversation/<user_to_id>', methods=['GET'])
def conversation(user_to_id):
    user_from_id = session['logged_user']
    db_session = db.getSession(engine)

    sent_messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_from_id).filter(
        entities.Message.user_to_id == user_to_id
    )
    received_messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_to_id).filter(
        entities.Message.user_to_id == user_from_id
    )
    raw_data = list(sent_messages) + list(received_messages)
    data = json.dumps(raw_data, cls=connector.AlchemyEncoder)
    return render_template('conversation.html', messages=json.loads(data))


@app.route('/users', methods=['POST'])
def create_user():
    data = json.loads(request.data)
    user = entities.User(
        email=data['email'],
        fullname=data['fullname'],
        username=data['username'],
        password=data['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    message = {'message': 'You have been registered!'}
    return jsonify(message), 201


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        payload = json.dumps(user, cls=connector.AlchemyEncoder)
        return Response(payload, status=200, mimetype='application/json')

    message = {'message': 'Not Found'}
    return jsonify(message), 404


@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data['username']
    password = data['password']

    db_session = db.getSession(engine)

    try:
        user = db_session.query(entities.User)\
            .filter(entities.User.username == username)\
            .filter(entities.User.password == password).one()
        session['logged_user'] = user.id
        message = {'message': 'Authorized'}
        return jsonify(message), 200
    except Exception:
        message = {'message': 'Unauthorized'}
        return jsonify(message), 401


@app.route('/current', methods=['GET'])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id == session['logged_user']).first()
    return Response(json.dumps(user, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/users', methods=['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = dbResponse[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    session = db.getSession(engine)
    user = session.query(entities.User).filter(entities.User.id == id).first()
    data = json.loads(request.form['values'])
    for key in data.keys():
        setattr(user, key, data[key])
    session.add(user)
    session.commit()
    return 'Updated User'


@app.route('/users', methods=['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    user = session.query(entities.User).filter(entities.User.id == id).one()
    session.delete(user)
    session.commit()
    return 'Deleted User'


@app.route('/messages/<id>', methods=['GET'])
def get_message(id):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(
        entities.Message.id == id)
    for message in messages:
        payload = json.dumps(message, cls=connector.AlchemyEncoder)
        return Response(payload, status=200, mimetype='application/json')

    message = {'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/messages', methods=['GET'])
def get_messages():
    sessionc = db.getSession(engine)
    messages = sessionc.query(entities.Message)
    data = messages[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/messages', methods=['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(
        entities.Message.id == id).first()
    data = json.loads(request.form['values'])
    for key in data.keys():
        setattr(message, key, data[key])
    session.add(message)
    session.commit()
    return 'Updated Message'


@app.route('/messages', methods=['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    message = session.query(entities.Message).filter(
        entities.Message.id == id).one()
    session.delete(message)
    session.commit()
    return 'Deleted Message'


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    content = data['content']
    user_to_id = data['user_to_id']
    user_from_id = session['logged_user']
    db_session = db.getSession(engine)
    add = entities.Message(
        content=content,
        sent_on=datetime.datetime.now(),
        user_from_id=user_from_id,
        user_to_id=user_to_id
    )
    db_session.add(add)
    db_session.commit()
    message = {'message': 'Message sent succesfully'}
    return jsonify(message), 200


@app.route('/groups', methods=['POST'])
def create_group():
    c = json.loads(request.data)
    group = entities.Group(name=c['name'])
    session_db = db.getSession(engine)
    session_db.add(group)
    session_db.commit()
    return 'Created Group'


@app.route('/groups/<id>', methods=['GET'])
def read_group(id):
    session_db = db.getSession(engine)
    group = session_db.query(entities.Group).filter(
        entities.Group.id == id).first()
    data = json.dumps(group, cls=connector.AlchemyEncoder)
    return Response(data, status=200, mimetype='application/json')


@app.route('/groups', methods=['GET'])
def get_all_groups():
    session_db = db.getSession(engine)
    dbResponse = session_db.query(entities.Group)
    data = dbResponse[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder),
                    mimetype='application/json')


@app.route('/groups/<id>', methods=['PUT'])
def update_group(id):
    session_db = db.getSession(engine)
    group = session_db.query(entities.Group).filter(
        entities.Group.id == id).first()
    c = json.loads(request.data)

    for key in c.keys():
        setattr(group, key, c[key])
    session.add(group)
    session.commit()
    return 'Updated GROUP'


@app.route('/groups/<id>', methods=['DELETE'])
def delete_group(id):
    session_db = db.getSession(engine)
    user = session_db.query(entities.Group).filter(
        entities.Group.id == id).one()
    session_db.delete(user)
    session_db.commit()
    return 'Deleted User'


if __name__ == '__main__':
    app.secret_key = '..'
    app.run(debug=True, port=8000, threaded=True, host=('127.0.0.1'))