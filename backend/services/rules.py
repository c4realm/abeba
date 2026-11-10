"""Charter defaults. A group's latest GroupTerms.terms_json overrides these keys."""
from decimal import Decimal

DEFAULT_RULES = {
    "grace_days": 2,
    "cure_days": 3,
    "fee_rate": "0.05",
    "fee_cap": "0.10",
    "premium_rate": "0.02",
    "holdback_rates": {"early": "0.30", "middle": "0.10", "late": "0.00"},
    "holdback_cap": "0.50",
}


def get_rules(group) -> dict:
    rules = dict(DEFAULT_RULES)
    terms = group.terms.order_by("-version").first()
    if terms:
        rules.update(terms.terms_json)
    return rules


def D(value) -> Decimal:
    return Decimal(str(value))
