/register (ok)
    -  POST: cadastrar usuário
        - args: username (que é CPF/CNPJ), password, id_cliente, e args do cliente/estabelecimento

/login (ok)
    - POST: login
        - args: username, password
        - retorno: jwt, refresh_token, message

/logout (ok)
    /access: invalida token
        - POST
            - args: jwt
            - retorno: message
    /refresh: invalida refresh token
        - POST
            - args: jwt, refresh_token
            - retorno: message

/token/refresh (ok)
    -  POST: token refresh
        - args: refresh_token

/cliente/fila
    - POST: cadastrar cliente em fila
        - args: id_fila, jwt
        - retorno: message, posicao, tempo_espera_atual
    - GET: pegar filas de cliente
        - args: jwt
        - retorno: filas {id_fila,nome,qtd_pessoas,tempo_espera_atual(do usuario),estabelecimento,posicao}
    - DELETE: cliente desinscrever de fila
        - args: jwt, id_fila
        - retorno: message
/fila
    - POST: cadastrar fila
        - args: jwt, args da fila
        - retorno: message
    - GET: pegar filas de um estabelecimento
        - args: id_fila (caso busca por única fila), estabelecimento_id (null=todas as filas)
        - retorno: filas {id_fila,nome,qtd_pessoas,tempo_espera_atual,estabelecimento}
    - DELETE: apagar fila
        - args: jwt, id_fila
        - retorno: message
        