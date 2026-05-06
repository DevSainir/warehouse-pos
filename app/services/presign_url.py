from app.integrations.s3 import presign_get_url


def build_image_urls(images: list[str] | None) -> list[str] | None:
    if not images:
        return None
    return [presign_get_url(key) for key in images if key]


def to_shop_product_out(product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "sale_price": product.sale_price,
        "quantity": product.quantity,
        "discount_percent": product.discount_percent,
        "final_customer_price": product.final_customer_price,
        "image_urls": build_image_urls(getattr(product, "images", None)),
        "categories": product.categories,
    }


def to_shop_product_category_out(product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "quantity": product.quantity,
        "sale_price": product.sale_price,
        "discount_percent": product.discount_percent,
        "final_customer_price": product.final_customer_price,
        "image_urls": build_image_urls(getattr(product, "images", None)),
    }