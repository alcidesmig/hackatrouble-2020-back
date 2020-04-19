from flask_restful import Resource, reqparse
from flask_api import status
from models import *
from flask_jwt_extended import jwt_required, get_jwt_identity

parser = reqparse.RequestParser()
parser_args = ['id_fila', 'nome', 'horario_abertura', 'horario_fechamento',
               'tempo_espera_indicado']
for i in parser_args:
    parser.add_argument(i)
parser.add_argument('usar_tempo_gerado', type=bool)

class inscricao_cliente_fila(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        fila = db.session.query(Fila).filter_by(int(data['id_fila'])).first()
        user = User.find_by_username(get_jwt_identity())
        if fila != int(data['id_fila']):
            return {
                'message': 'A fila na qual você tentou se inscrever deixou de existir',
            }, 200
        if not fila:
            return {
                'message': 'Fila inexistente.'
            }, 500
        if user.is_cliente and datetime.now().time() < fila.horario_abertura:
            if fila not in user.cliente.filas:
                user.cliente.filas.append(fila)
                if fila.usar_tempo_gerado:
                    fila.tempo_espera_atual = fila.tempo_espera_atual + fila.tempo_espera_gerado
                    # hora entrada = default
                else:
                    fila.tempo_espera_atual = fila.tempo_espera_atual + fila.tempo_espera_indicado
                db.session.add(user)
                db.session.add(fila)
                db.session.commit()
                return {
                    'message': 'Inscrito com sucesso!',
                }, 500
            else:
                return {
                    'message': 'Você já está inscrito nessa fila!',
                }, 500
        else:
            return {
                'message': 'Operação não permitida.'
            }, 403

    @jwt_required
    def get(self):
        data = parser.parse_args()
        filas = User.find_by_username(get_jwt_identity()).cliente.filas
        return {
            'filas:': filas
        }, 200
        #todo delete

    @jwt_required
    def delete(self):
        data = parser.parse_args()
        user = User.find_by_username(get_jwt_identity())
        if user.is_cliente:
            cliente = user.cliente
            fila = db.session.query(Fila).filter_by(int(data['id_fila'])).first()
            if fila not in cliente.filas:
                return {
                    'message': 'Operação não permitida'
                }, 403
            cliente.filas.remove(fila)
            if fila.usar_tempo_gerado:
                fila.tempo_espera_atual = fila.tempo_espera_atual - fila.tempo_espera_gerado
            else:
                fila.tempo_espera_atual = fila.tempo_espera_atual - fila.tempo_espera_indicado
            db.session.add(fila)
            db.session.add(cliente)
            db.session.commit()
            return {
                'message': 'Fila apagada!'
            }, 200
        else:
            return {
               'message': 'Operação não permitida'
            }, 403

class fila(Resource):
    @jwt_required
    def post(self):
        data = parser.parse_args()
        user = User.find_by_username(get_jwt_identity())
        if not user.is_cliente:
            estab = user.estabelecimento

            h, m = map(int, data['horario_abertura'].split(':'))
            horario_abertura = datetime.timedelta(hours=h, minutes=m)
            h, m = map(int, data['horario_fechamento'].split(':'))
            horario_fechamento = datetime.timedelta(hours=h, minutes=m)

            fila = Fila(
                nome=data['nome'], 
                descricao=data['descricao'],
                horario_abertura=horario_abertura,
                horario_fechamento=horario_fechamento,
                tempo_espera_indicado=data['tempo_espera_indicado'],
                tempo_espera_gerado=data['tempo_espera_indicado'],
                usar_tempo_gerado=data['usar_tempo_gerado']
            )

            estab.filas.append(fila)
            db.session.add(fila)
            db.session.add(estab)
            db.session.commit()
            return {
                'message': 'Fila criada com sucesso'
            }, 200
        else:
            return {
                'message': 'Operação não permitida.'
            }, 403

    @jwt_required
    def get(self): 
        data = parser.parse_args()
        filas = []
        if data['id_fila'] is not None:
            filas = db.session.query(Fila).filter_by(int(data['id_fila'])).first()
        else:
            filas = db.session.query(Fila).all()
        return {
            'filas': filas
        }, 200

    @jwt_required
    def delete(self):
        data = parser.parse_args()
        user = User.find_by_username(get_jwt_identity())
        if not user.is_cliente:
            estab = user.estabelecimento
            fila = db.session.query(Fila).filter_by(int(data['id_fila'])).first()
            if fila not in estab.filas:
                return {
                           'message': 'Operação não permitida'
                    }, 403
            estab.filas.remove(fila)
            for i in fila.clientes: #todo: verificar cascade sqlalchemy
                i.filas.remove(fila)
                db.session.add(i)
                #todo notificação: fila removida
            db.session.add(estab)
            db.session.commit()
            return {
                'message': 'Fila apagada!'
            }, 200
        else:
            return {
                'message': 'Operação não permitida'
            }, 403