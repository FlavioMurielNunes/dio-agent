"""Verificação temporária: injeção por concatenação vs. consulta parametrizada."""

import app

app.init_db()

payload = "' OR '1'='1"

with app.connect() as conn:
    concat = "SELECT username FROM users WHERE username = '" + payload + "'"
    print("SQL (concat):", concat)
    print("concat ->", conn.execute(concat).fetchall())

    fixed = "SELECT username FROM users WHERE username = ? AND password = ?"
    print("param (ataque) ->", conn.execute(fixed, (payload, payload)).fetchall())
    print("param (login valido) ->", conn.execute(fixed, ("admin", "admin789")).fetchall())
