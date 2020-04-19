from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'



app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

import src.views, src.resources_login as login, src.resources_user as user_api, models

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api = Api(app)

api.add_resource(login.UserRegistration, '/register')
api.add_resource(login.UserLogin, '/login')
api.add_resource(login.UserLogoutAccess, '/logout/access')
api.add_resource(login.UserLogoutRefresh, '/logout/refresh')
api.add_resource(login.TokenRefresh, '/token/refresh')

#api.add_resource(login.AllUsers, '/users')
#api.add_resource(login.SecretResource, '/secret')

api.add_resource(user_api.cliente_fila, '/cliente/fila')
api.add_resource(user_api.crud_fila, '/fila')
api.add_resource(user_api.visualizar_ordem_fila, '/fila/ordem')
api.add_resource(user_api.prox_da_fila, '/fila/proximo') #testar
api.add_resource(user_api.operacao_fila, '/fila/atendimento-encerrado') #testar
api.add_resource(user_api.api_estabelecimento, '/estabelecimento')

