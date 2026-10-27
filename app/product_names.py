import re


def normalize_product_name(value: str) -> str:
    return re.sub(r" {2,}", " ", value).strip(" ")
