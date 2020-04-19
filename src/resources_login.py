from flask_restful import Resource, reqparse
from flask_api import status
from models import *
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'Este campo não pode ser nulo', required = True)
parser.add_argument('password', help = 'Este campo não pode ser nulo', required = True)
parser.add_argument('is_cliente', type=bool)
parser.add_argument('nome_completo')
parser.add_argument('celular')
parser.add_argument('data_nasc')
parser.add_argument('sexo')
parser.add_argument('email')
parser.add_argument('preferencial', type=bool)
parser.add_argument('horario_abertura')
parser.add_argument('horario_fechamento')
parser.add_argument('endereco')
parser.add_argument('cep')
parser.add_argument('categoria_id')

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        if User.find_by_username(data['username']):
            return {'message': 'O código (CPF/CNPJ) já está cadastrado!'}
        user = User(username = data['username'], senha = User.generate_hash(data['password']))
        print(data)
        try:
            if (data['is_cliente']):
                user.is_cliente = True
                db.session.add(user)
                print("user_add")
                cliente = Cliente(id_user=user.id, nome_completo=data['nome_completo'], celular=data['celular'],
                                  data_nasc=data['data_nasc'], sexo=data['sexo'], email=data['email'],
                                  preferencial=data['preferencial'])
                print("ok")
                db.session.add(cliente)
            else:
                user.is_cliente = False
                db.session.add(user)
                h, m = map(int, data['horario_abertura'].split(':'))
                horario_abertura = datetime.timedelta(hours=h, minutes=m)
                h, m = map(int, data['horario_fechamento'].split(':'))
                horario_fechamento = datetime.timedelta(hours=h, minutes=m)

                estabelecimento = Estabelecimento(id_user=user.id, nome=data['nome'],
                                                  horario_abertura=horario_abertura,
                                                  horario_fechamento=horario_fechamento,
                                                  email=data['email'], endereco=data['endereco'],
                                                  cep=data['cep'], categoria_id=data['categoria_id'])
                db.session.add(estabelecimento)
            
            db.session.commit()
            
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            
            return {
                'message': 'Usuário {} criado.'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
            
            # return status.HTTP_200_OK
        except:
            return {
                'message': 'Erro desconhecido'
            }, 500

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
                'message': 'Olá, {}!'.format(user.username),
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
            return {'message': 'Usuário deslogado'}
        except:
            return {'message': 'Erro desconhecido'}, 500


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