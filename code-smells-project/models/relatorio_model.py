from database import get_db
from utils.constants import DISCOUNT_TIERS


def vendas() -> dict:
    row = get_db().execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
               COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
               COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
          FROM pedidos
        """
    ).fetchone()

    total_pedidos = row["total_pedidos"]
    faturamento = row["faturamento"]

    discount = 0
    for threshold, rate in DISCOUNT_TIERS:
        if faturamento > threshold:
            discount = faturamento * rate
            break

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(discount, 2),
        "faturamento_liquido": round(faturamento - discount, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
