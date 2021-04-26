from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.users import User
from data.users_parser import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify(
            {
                'user': user.to_dict(
                    only=('id', 'username', 'name', 'surname', 'work', 'email', 'phone_number')
                )
            }
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(
                        only=('id', 'username', 'name', 'surname', 'work', 'email',
                              'phone_number'))
                        for item in users]
            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['username'],
            name=args['name'],
            age=args['surname'],
            position=args['work'],
            speciality=args['email'],
            address=args['phone_number'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
