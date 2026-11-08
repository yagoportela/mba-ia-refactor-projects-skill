from database import get_db


def counts() -> dict:
    connection = get_db()
    return {
        "produtos": connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
        "usuarios": connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "pedidos": connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
    }
