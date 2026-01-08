from datetime import datetime
from src.services.validators import (
    require_nonempty, validate_email, validate_phone, validate_positive_int, validate_float, parse_datetime
)
from src.services.exceptions import ValidationError
from typing import Optional

def ask(prompt: str) -> str:
    return input(prompt).strip()

def ask_optional(prompt: str) -> Optional[str]:
    v = input(prompt).strip()
    return v if v else None

def pause():
    input("\nPokračuj Enterem...")

def print_table(rows: list[dict]):
    if not rows:
        print("(žádná data)")
        return
    cols = list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c,''))) for r in rows)) for c in cols}
    header = " | ".join(f"{c:<{widths[c]}}" for c in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(f"{str(r.get(c,'')):<{widths[c]}}" for c in cols))

def ask_enum(prompt: str, allowed: list[str], default: Optional[str] = None) -> str:
    allowed_upper = [a.upper() for a in allowed]
    while True:
        suffix = f" ({'/'.join(allowed_upper)})"
        if default:
            suffix += f" [default {default}]"
        val = ask(prompt + suffix + ": ").upper()
        if not val and default:
            return default.upper()
        if val in allowed_upper:
            return val
        print("Neplatná hodnota.")

def ask_phone_optional():
    phone = ask_optional("Telefon (volitelné): ")
    if phone:
        return validate_phone(phone)
    return None

def ask_style_ids(style_rows: list[dict]) -> list[int]:
    if not style_rows:
        return []
    print("\nDostupné styly:")
    for s in style_rows:
        print(f"  {s['style_id']}: {s['name']} (base_price={s['base_price']})")
    raw = ask_optional("Vyber style_id oddělené čárkou (např. 1,3) nebo prázdné: ")
    if not raw:
        return []
    try:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        raise ValidationError("Špatný formát style_id. Použij čísla oddělená čárkou.")
