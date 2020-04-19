from flask_restful import Resource, reqparse
from flask_api import status
from models import User

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'Este campo não pode ser nulo', required = True)
parser.add_argument('password', help = 'Este campo não pode ser nulo', required = True)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        if User.find_by_username(data['username']):
            return {'message': 'O código (CPF/CNPJ) já está cadastrado!'}
        user = User(username = data['username'], password = User.generate_hash(data['password']))
        try:
            user.save_db() #todo check username
            return status.HTTP_200_OK
        except:
            return status.HTTP_500_INTERNAL_SERVER_ERROR


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = User.find_by_username(data['username'])
        if not user:
            return {'message': 'O usuário não existe.'}
        
        if User.verify_hash(data['password'], user.password):
            return {'message': 'Login realizado com sucesso!'}
        else:
            return {'message': 'Senha inválida!'}

class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refresh'}


class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }