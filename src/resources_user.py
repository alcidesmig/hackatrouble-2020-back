from flask_restful import Resource, reqparse
from flask_api import status
from models import *
from flask_jwt_extended import jwt_required, get_jwt_identity

parser = reqparse.RequestParser()

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
