from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

cliente_filas = db.Table('relacao_cliente_filas',
    db.Column('id_fila', db.Integer, db.ForeignKey('fila.id')),
    db.Column('id_cliente', db.Integer, db.ForeignKey('cliente.id'))
)

# fonte 13

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), nullable=False)
    nome_completo = db.Column(db.String(96), nullable=False)
    celular = db.Column(db.String(16), nullable=True)
    data_nasc = db.Column(db.String(8), nullable=False)
    sexo = db.Column(db.String(16), nullable=False) # choices
    senha = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(32), nullable=True)
    email_verificado = db.Column(db.Boolean, default=0)
    
    # backref de filas
    def __repr__(self):
        return self.id

class Estabelecimento(db.Model):
    __tablename__ = 'estabelecimento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    horario_abertura = db.Column(db.String(16), nullable=False)
    horario_fechamento = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(32))
    senha = db.Column(db.String(512), nullable=False)
    endereco = db.Column(db.String(128), nullable=False)
    cep = db.Column(db.String(8))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    categorias = db.relationship('Categoria', back_populates="estabelecimento")
    filas = db.relationship("Fila", back_populates="estabelecimento")

    def __repr__(self):
        return self.id

class Fila(db.Model):
    __tablename__ = 'fila'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    descricao = db.Column(db.String(256), nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimento.id'))
    estabelecimento = db.relationship("Estabelecimento", back_populates="filas")
    horario_abertura = db.Column(db.String(16), nullable=False)
    horario_fechamento = db.Column(db.String(16), nullable=False)
    clientes = db.relationship("Cliente",
                    secondary=cliente_filas,
                    backref="filas")
    tempo_espera_indicado = db.Column(db.Float, default=0)
    tempo_espera_gerado = db.Column(db.Float, default=0)

    def __repr__(self):
        return self.id

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(96), nullable=False)
    estabelecimentos = db.relationship("Estabelecimento", back_populates="categoria")

    def __repr__(self):
        return self.id
    
