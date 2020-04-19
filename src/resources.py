from flask_restful import Resource, reqparse
from flask_api import status
from models import *
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'Este campo não pode ser nulo', required = True)
parser.add_argument('password', help = 'Este campo não pode ser nulo', required = True)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        if User.find_by_username(data['username']):
            return {'message': 'O código (CPF/CNPJ) já está cadastrado!'}
        user = User(username = data['username'], senha = User.generate_hash(data['password']))
        
        try:
            user.save_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity = data['username'])

            return {
                'message': 'Usuário {} criado.'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
            # return status.HTTP_200_OK
        except:
            return status.HTTP_500_INTERNAL_SERVER_ERROR


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        user = User.find_by_username(data['username'])
        if not user:
            return {'message': 'O usuário não existe.'}
        
        if User.verify_hash(data['password'], user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'Logged in as {}'.format(user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            #return {'message': 'Login realizado com sucesso!'}
        else:
            return {'message': 'Senha inválida!'}

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'Teste': 'Ok.'
        }