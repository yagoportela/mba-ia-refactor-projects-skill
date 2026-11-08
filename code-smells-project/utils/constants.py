ORDER_STATUSES = ("pendente", "aprovado", "enviado", "entregue", "cancelado")
PRODUCT_CATEGORIES = (
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
)
USER_TYPES = ("cliente", "admin", "gerente")

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 200
MIN_PRODUCT_NAME_LENGTH = 2
MAX_PRODUCT_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MIN_PASSWORD_LENGTH = 6
MAX_ITEMS_PER_ORDER = 100

DISCOUNT_TIERS = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)
