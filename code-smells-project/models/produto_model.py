from database import get_db, transaction

COLUMNS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _to_dict(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def list_all(page: int, per_page: int):
    connection = get_db()
    total = connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    rows = connection.execute(
        f"SELECT {COLUMNS} FROM produtos ORDER BY id LIMIT ? OFFSET ?",
        (per_page, (page - 1) * per_page),
    ).fetchall()
    return [_to_dict(row) for row in rows], total


def count_all() -> int:
    return get_db().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]


def get_by_id(produto_id: int):
    row = get_db().execute(
        f"SELECT {COLUMNS} FROM produtos WHERE id = ?",
        (produto_id,),
    ).fetchone()
    return _to_dict(row) if row else None


def create(data: dict) -> int:
    connection = get_db()
    with transaction(connection):
        cursor = connection.execute(
            """
            INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["nome"],
                data["descricao"],
                data["preco"],
                data["estoque"],
                data["categoria"],
            ),
        )
        return cursor.lastrowid


def update(produto_id: int, data: dict) -> bool:
    connection = get_db()
    with transaction(connection):
        cursor = connection.execute(
            """
            UPDATE produtos
               SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
             WHERE id = ?
            """,
            (
                data["nome"],
                data["descricao"],
                data["preco"],
                data["estoque"],
                data["categoria"],
                produto_id,
            ),
        )
        return cursor.rowcount > 0


def delete(produto_id: int) -> bool:
    connection = get_db()
    with transaction(connection):
        cursor = connection.execute(
            "DELETE FROM produtos WHERE id = ?",
            (produto_id,),
        )
        return cursor.rowcount > 0


def search(
    termo: str | None,
    categoria: str | None,
    preco_min: float | None,
    preco_max: float | None,
    page: int,
    per_page: int,
):
    connection = get_db()
    where = ["1=1"]
    params: list = []

    if termo:
        where.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        where.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        where.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        where.append("preco <= ?")
        params.append(preco_max)

    where_sql = " AND ".join(where)
    total = connection.execute(
        f"SELECT COUNT(*) FROM produtos WHERE {where_sql}",
        params,
    ).fetchone()[0]

    rows = connection.execute(
        f"""
        SELECT {COLUMNS}
          FROM produtos
         WHERE {where_sql}
         ORDER BY id
         LIMIT ? OFFSET ?
        """,
        (*params, per_page, (page - 1) * per_page),
    ).fetchall()
    return [_to_dict(row) for row in rows], total
