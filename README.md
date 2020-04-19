/cliente/fila
    - POST: cadastrar cliente em fila
        - args: id_fila, access_token
        - retorno: message
    - GET: 
        - pegar filas de cliente
            - args: access_token
            - retorno: filas
        
/register 
    -  POST: cadastrar usuário
        - args: username (que é CPF/CNPJ), password, is_cliente, e args do cliente/estabelecimento

/login
    - POST: login
        - args: username, password
        - retorno: access_token, refresh_token, message

/logout
    /access: invalida token
        - POST
            - args: access_token
            - retorno: message
    /refresh: invalida refresh token
        - POST
            - args: access_token, refresh_token
            - retorno: message

/token/refresh
    -  POST: token refresh
        - args: refresh_token


