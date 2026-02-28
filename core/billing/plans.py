# Credit pack definitions.
# Each pack is a one-time purchase via Lemon Squeezy.
# Key = pack name, value = credits awarded on purchase.

CREDIT_PACKS = {
    "starter": {"credits": 5,  "price_usd": 9},
    "growth":  {"credits": 15, "price_usd": 19},
    "studio":  {"credits": 50, "price_usd": 49},
}


def get_credits_for_pack(pack_name: str) -> int:
    pack = CREDIT_PACKS.get(pack_name)
    if not pack:
        raise ValueError(f"Unknown credit pack: {pack_name}")
    return pack["credits"]
