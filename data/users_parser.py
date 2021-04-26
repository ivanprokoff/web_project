from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True, type=int)
parser.add_argument('work', required=True)
parser.add_argument('email', required=True)
parser.add_argument('phone_number', required=True)
parser.add_argument('password', required=True)
