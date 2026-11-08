from database import get_db, transaction
from utils.errors import ApiError


def _group_orders(rows) -> list[dict]:
    orders: dict[int, dict] = {}
    for row in rows:
        order_id = row["pedido_id"]
        if order_id not in orders:
            orders[order_id] = {
                "id": row["pedido_id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            orders[order_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(orders.values())


def _list_orders(where_sql: str, params: tuple, page: int, per_page: int):
    connection = get_db()
    total = connection.execute(
        f"SELECT COUNT(*) FROM pedidos {where_sql}",
        params,
    ).fetchone()[0]

    rows = connection.execute(
        f"""
        SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
          FROM (
                SELECT id, usuario_id, status, total, criado_em
                  FROM pedidos
                  {where_sql}
                 ORDER BY id
                 LIMIT ? OFFSET ?
               ) p
          LEFT JOIN itens_pedido i ON i.pedido_id = p.id
          LEFT JOIN produtos pr ON pr.id = i.produto_id
         ORDER BY p.id, i.id
        """,
        (*params, per_page, (page - 1) * per_page),
    ).fetchall()

    return _group_orders(rows), total


def list_by_usuario(usuario_id: int, page: int, per_page: int):
    return _list_orders("WHERE usuario_id = ?", (usuario_id,), page, per_page)


def list_all(page: int, per_page: int):
    return _list_orders("", (), page, per_page)


def get_by_id(pedido_id: int):
    rows = get_db().execute(
        """
        SELECT p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
          FROM pedidos p
          LEFT JOIN itens_pedido i ON i.pedido_id = p.id
          LEFT JOIN produtos pr ON pr.id = i.produto_id
         WHERE p.id = ?
        """,
        (pedido_id,),
    ).fetchall()
    orders = _group_orders(rows)
    return orders[0] if orders else None


def create(usuario_id: int, itens: list[dict]) -> dict:
    connection = get_db()

    requested: dict[int, int] = {}
    for item in itens:
        product_id = int(item["produto_id"])
        quantity = int(item["quantidade"])
        requested[product_id] = requested.get(product_id, 0) + quantity

    placeholders = ",".join("?" for _ in requested)
    rows = connection.execute(
        f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
        tuple(requested),
    ).fetchall()
    products = {row["id"]: row for row in rows}

    for product_id, quantity in requested.items():
        product = products.get(product_id)
        if product is None:
            raise ApiError(f"Produto {product_id} não encontrado", 400)
        if product["estoque"] < quantity:
            raise ApiError(f"Estoque insuficiente para {product['nome']}", 400)

    total = sum(
        products[product_id]["preco"] * quantity
        for product_id, quantity in requested.items()
    )

    with transaction(connection):
        cursor = connection.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, "pendente", round(total, 2)),
        )
        order_id = cursor.lastrowid

        for item in itens:
            product_id = int(item["produto_id"])
            connection.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    product_id,
                    int(item["quantidade"]),
                    products[product_id]["preco"],
                ),
            )

        for product_id, quantity in requested.items():
            updated = connection.execute(
                """
                UPDATE produtos
                   SET estoque = estoque - ?
                 WHERE id = ? AND estoque >= ?
                """,
                (quantity, product_id, quantity),
            ).rowcount
            if updated == 0:
                raise ApiError(f"Estoque insuficiente para o produto {product_id}", 400)

    return {"pedido_id": order_id, "total": round(total, 2)}


def update_status(pedido_id: int, status: str) -> bool:
    connection = get_db()
    with transaction(connection):
        cursor = connection.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (status, pedido_id),
        )
        return cursor.rowcount > 0
