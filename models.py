from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256 as sha256
from app import app
from datetime import datetime

#todo lazy queries

db = SQLAlchemy(app)


# fonte 13
@app.before_first_request
def create_tables():
#    return
 #   db.drop_all()
    db.create_all()

class ClienteFilas(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    id_fila = db.Column(db.Integer, db.ForeignKey('fila.id'))
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    
    clientes = db.relationship("Cliente", back_populates='cliente_filas')
    filas = db.relationship("Fila", back_populates='cliente_filas')
    
    posicao_absoluta = db.Column('posicao_absoluta', db.Integer, default=0)
    hora_entrada = db.Column('hora_entrada', db.Time, default=datetime.now().time())


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True) #cpf ou cnpj
    senha = db.Column(db.String(512), nullable=False)
    
    is_cliente = db.Column(db.Boolean)

    cliente = db.relationship("Cliente", uselist=False, back_populates="user")
    estabelecimento = db.relationship("Estabelecimento", uselist=False, back_populates="user")

    
    def save_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), User.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    # backref de filas
    def __repr__(self):
        return self.id

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(96), nullable=False)
    celular = db.Column(db.String(16), nullable=True)
    data_nasc = db.Column(db.String(8), nullable=False)
    sexo = db.Column(db.String(16), nullable=False)  # choices
    email = db.Column(db.String(32), nullable=True)
    email_verificado = db.Column(db.Boolean, default=0)
    preferencial = db.Column(db.Integer, default=0)

    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="cliente")
    
    cliente_filas = db.relationship("ClienteFilas", back_populates="clientes")

    # backref de filas
    def __repr__(self):
        return self.id


class Estabelecimento(db.Model):
    __tablename__ = 'estabelecimento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    horario_abertura = db.Column(db.Time, nullable=False)
    horario_fechamento = db.Column(db.Time, nullable=False)
    email = db.Column(db.String(32))
    endereco = db.Column(db.String(128), nullable=False)
    cep = db.Column(db.String(8))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)
    categoria = db.relationship('Categoria', back_populates="estabelecimento")
    filas = db.relationship("Fila", back_populates="estabelecimento")

    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="estabelecimento")

    #todo dias funcionamento

    def __repr__(self):
        return self.id


class Fila(db.Model):
    __tablename__ = 'fila'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    descricao = db.Column(db.String(256), nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimento.id'))
    estabelecimento = db.relationship("Estabelecimento", back_populates="filas")
    horario_abertura = db.Column(db.Time, nullable=False)
    horario_fechamento = db.Column(db.Time, nullable=False)

    cliente_filas = db.relationship("ClienteFilas", back_populates="filas")

    tempo_espera_indicado = db.Column(db.Float, default=0) # Indivídual
    tempo_espera_gerado = db.Column(db.Float, default=0)   # Indivídual
    usar_tempo_gerado = db.Column(db.Boolean, default=True)

    ultima_posicao = db.Column(db.Integer, default=0)
    
    clientes_atendidos = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return self.id


class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    estabelecimento = db.relationship("Estabelecimento", back_populates="categoria")

    def __repr__(self):
        return self.id


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)