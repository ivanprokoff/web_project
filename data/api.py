import flask
from flask import jsonify, request

from data import db_session
from data.users import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(
                    only=(
                        'id', 'username', 'name', 'surname', 'work', 'email', 'phone_number'))
                    for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': user.to_dict(
                only=('id', 'username', 'name', 'surname', 'work', 'email', 'phone_number')
            )
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'username', 'name', 'surname', 'work', 'email', 'phone_number',
                  'password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    # if db_sess.query(User).filter_by(id=request.json['id']).first():
    #     return jsonify({'error': 'Id already exists'})
    user = User(
        surname=request.json['username'],
        name=request.json['name'],
        age=request.json['surname'],
        position=request.json['work'],
        speciality=request.json['email'],
        address=request.json['phone_number'],
    )
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'Id does not exists'})

    if request.json.get('username'):
        user.surname = request.json['username']
    if request.json.get('name'):
        user.name = request.json['name']
    if request.json.get('surname'):
        user.age = request.json['surname']
    if request.json.get('work'):
        user.position = request.json['work']
    if request.json.get('email'):
        user.speciality = request.json['email']
    if request.json.get('phone_number'):
        user.address = request.json['phone_number']

    db_sess.commit()
    return jsonify({'success': 'OK'})
