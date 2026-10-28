"""
Laboratório de SQL Injection da DIO.

ATENÇÃO: ESTE CÓDIGO É INTENCIONALMENTE INSEGURO.

Ele existe para ser usado em um ambiente de estudo controlado (laboratório),
para você aprender a encontrar uma falha de SQL Injection e depois corrigi-la.
A consulta SQL é montada por concatenação de strings, sem parametrização, o que
permite ataques de SQL Injection.

Regras de uso:
- Rode apenas na sua máquina, nunca em servidor público ou com dados reais.
- Nunca reutilize este padrão de concatenação em código de verdade.
- Use dados fictícios (o script já cria usuários de teste).

Como executar:

    python app.py

O script cria o arquivo `lab.db` (SQLite) na mesma pasta, com alguns usuários
de teste, e abre um menu no terminal.

O objetivo do laboratório NÃO é decorar um payload de ataque. É entender por que
a falha existe e qual é a correção defensiva.
"""

import sqlite3

DATABASE = "lab.db"


# ---------------------------------------------------------------------------
# Camada de banco de dados
# ---------------------------------------------------------------------------


def connect() -> sqlite3.Connection:
    """Abre a conexão com o banco SQLite do laboratório."""
    return sqlite3.connect(DATABASE)


def init_db() -> None:
    """Cria a tabela de usuários e insere dados fictícios de teste."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """
        )

        # ON CONFLICT evita duplicar os usuários se o script rodar de novo.
        conn.execute(
            """
            INSERT INTO users (username, password, role) VALUES
                ('ana', 'senha123', 'user'),
                ('bruno', 'senha456', 'user'),
                ('admin', 'admin789', 'admin')
            ON CONFLICT (username) DO NOTHING
            """
        )


# ---------------------------------------------------------------------------
# Ponto 1 do laboratório: login vulnerável a SQL Injection
# ---------------------------------------------------------------------------


def authenticate(username: str, password: str) -> dict | None:
    """
    Verifica as credenciais de um usuário.

    >>> VULNERABILIDADE PROPOSITAL <<<

    A consulta abaixo é montada concatenando as entradas do usuário
    diretamente no texto do SQL. Ou seja, o que a pessoa digita passa a fazer
    parte do COMANDO enviado ao banco, e não de um DADO separado do comando.

    O `?` (placeholder) não é usado de propósito, para que você consiga
    reproduzir o problema no laboratório.

    Perguntas para você investigar (use a skill `vulnerability-analysis`):

    1. O que acontece se o campo de senha receber um trecho que "fecha" a
       string do SQL?
    2. Por que um trecho de comentário de SQL muda o comportamento da consulta?
    3. Qual é o impacto real de entrar como `admin` sem saber a senha?
    4. Como a mesma ideia funcionaria no campo de usuário?
    """
    query = (
        "SELECT id, username, role FROM users "
        "WHERE username = '" + username + "' AND password = '" + password + "' "
        "ORDER BY id DESC"
    )

    print("\n[depuração] SQL executado pelo banco:")
    print(f"  {query}")

    with connect() as conn:
        cursor = conn.execute(query)
        row = cursor.fetchone()

    if row is None:
        return None

    # ATENÇÃO (falha secundária proposital): a consulta usa fetchone(), então
    # devolvemos o primeiro registro encontrado. Se a injeção fizer a cláusula
    # WHERE ser sempre verdadeira, o filtro deixa de existir e o login é
    # aceito sem senha. Perceba que a saída pode até ser um usuário diferente
    # do que foi digitado: a injeção não respeitou a intenção do programador.
    # Uma correção correta resolve a raiz (parametrização), não o sintoma.
    return {"id": row[0], "username": row[1], "role": row[2]}


# ---------------------------------------------------------------------------
# Ponto 2 do laboratório: listagem de usuários vulnerável a SQL Injection
# ---------------------------------------------------------------------------


def search_users(term: str) -> list[tuple]:
    """
    Lista usuários cujo nome contenha o termo informado.

    >>> VULNERABILIDADE PROPOSITAL <<<

    Outra concatenação direta. Aqui a injeção consegue alterar o filtro e
    até acrescentar cláusulas que o programador não escreveu.

    Perguntas para você investigar:

    1. Qual é o impacto de listar TODOS os usuários ignorando o filtro?
    2. O problema muda se a coluna consultada for algo sensível (e-mail,
       documento, hash de senha)? Por quê?
    3. Qual é a diferença entre essa falha e a do login, em termos de
       confidencialidade da informação?
    """
    query = (
        "SELECT id, username, role FROM users "
        "WHERE username LIKE '%" + term + "%'"
    )

    print("\n[depuração] SQL executado pelo banco:")
    print(f"  {query}")

    with connect() as conn:
        cursor = conn.execute(query)
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Camada de interface (terminal)
# ---------------------------------------------------------------------------


def show_login() -> None:
    print("\n=== Login (vulnerável) ===")
    username = input("Usuário: ")
    password = input("Senha: ")

    user = authenticate(username, password)

    if user is None:
        print("Login falhou.")
        return

    print(
        f"Login realizado. Bem-vindo(a), {user['username']} "
        f"(perfil: {user['role']})."
    )


def show_search() -> None:
    print("\n=== Buscar usuários (vulnerável) ===")
    term = input("Digite parte do nome: ")

    rows = search_users(term)

    if not rows:
        print("Nenhum usuário encontrado.")
        return

    print(f"\n{len(rows)} usuário(s) encontrado(s):")
    for user_id, username, role in rows:
        print(f"  #{user_id} - {username} ({role})")


def print_menu() -> None:
    print(
        """
==========================================
 DIO - Laboratório de SQL Injection
==========================================
 1 - Fazer login
 2 - Buscar usuários
 3 - Listar todos os usuários
 0 - Sair
------------------------------------------
 Este sistema é INSEGURO de propósito.
 Use apenas para estudo local.
=========================================="""
    )


def main() -> None:
    init_db()
    print(f"Banco inicializado: {DATABASE}")

    while True:
        print_menu()
        option = input("Escolha uma opção: ").strip()

        if option == "1":
            show_login()
        elif option == "2":
            show_search()
        elif option == "3":
            with connect() as conn:
                rows = conn.execute(
                    "SELECT id, username, role FROM users"
                ).fetchall()
            print(f"\n{len(rows)} usuário(s) cadastrado(s):")
            for user_id, username, role in rows:
                print(f"  #{user_id} - {username} ({role})")
        elif option == "0":
            print("Até logo! Continue estudando segurança.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
