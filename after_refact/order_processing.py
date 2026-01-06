# ================== Константы ==================

DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21

# Купоны
COUPON_SAVE10 = "SAVE10"
COUPON_SAVE20 = "SAVE20"
COUPON_VIP = "VIP"

# Проценты и значения скидок
DISCOUNT_SAVE10 = 0.10

DISCOUNT_SAVE20_HIGH = 0.20   # для заказов >= 200
DISCOUNT_SAVE20_LOW = 0.05    # для заказов < 200

DISCOUNT_VIP_HIGH = 50        # для заказов >= 100
DISCOUNT_VIP_LOW = 10         # для заказов < 100

# Пороговые значения
THRESHOLD_SAVE20 = 200
THRESHOLD_VIP = 100


# ================== Разбор запроса ==================

def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


# ================== Валидация ==================

def validate_request(user_id, items, currency):
    if user_id is None:
        raise ValueError("user_id is required")

    if items is None:
        raise ValueError("items is required")

    if not isinstance(items, list):
        raise ValueError("items must be a list")

    if len(items) == 0:
        raise ValueError("items must not be empty")

    if currency is None:
        currency = DEFAULT_CURRENCY

    return currency


def validate_items(items):
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


# ================== Расчёты ==================

def calculate_subtotal(items):
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(subtotal, coupon):
    if not coupon:
        return 0

    if coupon == COUPON_SAVE10:
        return int(subtotal * DISCOUNT_SAVE10)

    if coupon == COUPON_SAVE20:
        if subtotal >= THRESHOLD_SAVE20:
            return int(subtotal * DISCOUNT_SAVE20_HIGH)
        return int(subtotal * DISCOUNT_SAVE20_LOW)

    if coupon == COUPON_VIP:
        if subtotal < THRESHOLD_VIP:
            return DISCOUNT_VIP_LOW
        return DISCOUNT_VIP_HIGH

    raise ValueError("unknown coupon")


def calculate_tax(amount):
    return int(amount * TAX_RATE)


# ================== Основной сценарий ==================

def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)

    currency = validate_request(user_id, items, currency)
    validate_items(items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)

    total_after_discount = max(0, subtotal - discount)

    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    order_id = f"{user_id}-{len(items)}-X"

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
