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

def get_pos_usuario(id_cliente, id_fila): #todo mover para utils
    posicao_absoluta_cliente = db.session.query(cliente_filas).filter_by(id_cliente=id_cliente, id_fila=i.id).first().posicao_absoluta_cliente
    clientes_filas = db.session.query(cliente_filas).filter_by(id_fila=i.id).all()

    cont_pos = 0
    for j in clientes_filas:
        if j.posicao_absoluta < posicao_absoluta_cliente:
            cont_pos += 1
    return cont_pos

class cliente_fila(Resource):
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
                tempo_espera_atual = 0
                if fila.usar_tempo_gerado:
                    tempo_espera_atual = len(user.cliente.filas) * fila.tempo_espera_gerado
                    # hora entrada = default
                else:
                    tempo_espera_atual = len(user.cliente.filas)* fila.tempo_espera_indicado
                db.session.add(user)
                fila.ultima_posicao = fila.ultima_posicao + 1
                db.session.add(fila)
                db.session.commit()

                fila_cliente = db.session.query(cliente_filas).filter_by(id_cliente=user.cliente.id, id_fila=fila.id).first()
                fila_cliente.posicao_absoluta = fila.ultima_posicao + 1
                posicao_rel = len(fila.clientes) - 1
                db.session.add(fila_cliente)
                db.session.commit()
                return {
                    'message': 'Inscrito com sucesso!',
                    'posicao': posicao_rel,
                    'tempo_espera_atual': tempo_espera_atual
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
        user = User.find_by_username(get_jwt_identity())
        filas = user.cliente.filas
        filas_final = []
        
        for i in filas:

            posicao = get_pos_usuario(user.cliente.id, i.id)

            tempo_espera_atual = 0
            
            if i.usar_tempo_gerado:
                tempo_espera_atual = i.tempo_espera_gerado * posicao
            else:
                tempo_espera_atual = i.tempo_espera_indicado * posicao

            filas_final.append({
                'id_fila': i.id,
                'nome': i.nome,
                'qtd_pessoas': len(i.clientes),
                'tempo_espera_atual': tempo_espera_atual,
                'estabelecimento': i.estabelecimento,
                'posicao': posicao,
            })
        return {
            'filas:': filas
        }, 200
        #todo delete

    @jwt_required #todo arrumar posicoes
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

class crud_fila(Resource):
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
            filas = db.session.query(Fila).filter_by(id=int(data['id_fila'])).first()
        elif data['estabelecimento_id'] is not None:
            filas = db.session.query(Fila).filter_by(estabelecimento_id=int(data['estabelecimento_id'])).all()
        else:
            filas = db.session.query(Fila).all()
        filas_final = []
        for i in filas:
            filas_final.append({
                'id_fila': i.id,
                'nome': i.nome,
                'qtd_pessoas': len(i.clientes),
                'tempo_espera_atual': i.tempo_espera_atual,
                'estabelecimento': i.estabelecimento
            })
        return {
            'filas': filas_final
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

#todo visualizar posição em fila: posicao_atual - clientes atendidos
#todo cliente entrou, cliente saiu, cliente faltou
#todo estabelecimento adiciona pessoa
#todo visualizar: proximo da fila, todas pessoas,
#todo edit estabelecimento
#todo get tempo_espera_fila

class api_estabelecimento(Resource):
    @jwt_required
    def put(self):
        data = parser.parse_args()
        user = User.find_by_username(get_jwt_identity())
        return None

   # @jwt_required
