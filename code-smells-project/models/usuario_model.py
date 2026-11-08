from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, transaction

PUBLIC_COLUMNS = "id, nome, email, tipo, criado_em"


def _public_dict(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def list_all(page: int, per_page: int):
    connection = get_db()
    total = connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    rows = connection.execute(
        f"SELECT {PUBLIC_COLUMNS} FROM usuarios ORDER BY id LIMIT ? OFFSET ?",
        (per_page, (page - 1) * per_page),
    ).fetchall()
    return [_public_dict(row) for row in rows], total


def count_all() -> int:
    return get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]


def get_by_id(usuario_id: int):
    row = get_db().execute(
        f"SELECT {PUBLIC_COLUMNS} FROM usuarios WHERE id = ?",
        (usuario_id,),
    ).fetchone()
    return _public_dict(row) if row else None


def get_by_email(email: str):
    row = get_db().execute(
        f"SELECT {PUBLIC_COLUMNS} FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()
    return _public_dict(row) if row else None


def create(nome: str, email: str, senha: str, tipo: str = "cliente") -> int:
    connection = get_db()
    with transaction(connection):
        cursor = connection.execute(
            """
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (?, ?, ?, ?)
            """,
            (nome, email, generate_password_hash(senha), tipo),
        )
        return cursor.lastrowid


def verify_credentials(email: str, senha: str):
    connection = get_db()
    row = connection.execute(
        """
        SELECT id, nome, email, senha, tipo, criado_em
          FROM usuarios
         WHERE email = ?
        """,
        (email,),
    ).fetchone()

    if row is None:
        return None

    stored = row["senha"]
    is_strong_hash = stored.startswith(("scrypt:", "pbkdf2:"))

    if is_strong_hash:
        valid = check_password_hash(stored, senha)
    elif stored == senha:
        valid = True
        with transaction(connection):
            connection.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(senha), row["id"]),
            )
    else:
        valid = False

    if not valid:
        return None

    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
