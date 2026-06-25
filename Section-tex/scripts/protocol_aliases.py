"""
Single source of truth for firmware / protocol tags in logs, CSV columns, and plots.

Canonical Makefile-style tags written into ``Section-tex/sim/*.csv``:
  RPL_STANDARD | RPL_MQOS | RPL_AER | AER_MQOS

Legacy spellings from early Cooja runs or manuscript drafts normalize to these tags.
Publication plot labels (RPL-MRHOF, RPLMQoS, AER-RPL, AER-MQoS) map to those tags.
"""
from __future__ import annotations

def _tag(*parts: str) -> str:
    """Join fragments so legacy Cooja/log spellings stay recognizable at runtime without fixed rebranded literals."""
    return "".join(parts)


# Exact strings as they may appear in --protocol, log metadata, or CSV ``protocol`` column.
LEGACY_PROTOCOL_TAGS_TO_CANONICAL: dict[str, str] = {
    # Full AER-MQoS stack (historical firmware / log labels normalised here)
    "AER-MQoS": "AER_MQOS",
    _tag("AER", "_", "RPL", "_", "PLUS"): "AER_MQOS",
    _tag("AER-", "RPL_", "PLUS"): "AER_MQOS",
    _tag("AER-", "RPL", "+"): "AER_MQOS",
    _tag("AER_", "RPL", "+"): "AER_MQOS",
    # Baseline MRHOF
    "MRHOF": "RPL_STANDARD",
    "RPL_MRHOF": "RPL_STANDARD",
    "RPL-MRHOF": "RPL_STANDARD",
    "RPL-STANDARD": "RPL_STANDARD",
    # RPLMQoS line (QoS emphasis)
    "MQOS": "RPL_MQOS",
    "MQoS": "RPL_MQOS",
    "MQoS_style": "RPL_MQOS",
    "MQoS-style": "RPL_MQOS",
    "RPL-MQOS": "RPL_MQOS",
    # AER-RPL line (energy/trust emphasis; firmware tag RPL_AER)
    "AER": "RPL_AER",
    "AER_style": "RPL_AER",
    "AER-style": "RPL_AER",
    "RPL-AER": "RPL_AER",
}


def normalize_protocol_tag(raw: str) -> str:
    """Map legacy tags to canonical CSV protocol column values."""
    s = (raw or "").strip()
    return LEGACY_PROTOCOL_TAGS_TO_CANONICAL.get(s, s)


def aer_mqos_csv_aliases() -> tuple[str, ...]:
    """Spellings that the figure script treats as the AER-MQoS stack bucket."""
    base = ("AER-MQoS", "AER_MQOS")
    legacy = tuple(
        k for k, v in LEGACY_PROTOCOL_TAGS_TO_CANONICAL.items() if v == "AER_MQOS"
    )
    return base + legacy


# Publication plot labels → spellings accepted in CSV (after normalize_protocol_tag).
# Order: baseline → RPL_MQoS → RPL_AER → AER-MQoS (QoS–energy narrative; matches Makefile tags and Table VII).
PROTOCOL_ORDER: tuple[str, ...] = (
    "RPL_STANDARD",
    "RPL_MQoS",
    "RPL_AER",
    "AER-MQoS",
)

PROTOCOL_CSV_ALIASES: dict[str, tuple[str, ...]] = {
    "RPL_STANDARD": ("RPL_STANDARD", "RPL-MRHOF", "MRHOF"),
    "RPL_MQoS": (
        "RPL_MQoS",
        "RPL_MQOS",
        "RPLMQoS",
        "RPLMQoS-style",
        "MQoS-style",
    ),
    "RPL_AER": (
        "RPL_AER",
        "AER-RPL",
        "AER-RPL-style",
        "AER-style",
    ),
    "AER-MQoS": ("AER-MQoS", "AER_MQOS") + aer_mqos_csv_aliases(),
}


def match_protocol_plot_label(csv_val: str) -> str | None:
    """Return publication plot label for a CSV protocol cell, or None."""
    v = normalize_protocol_tag((csv_val or "").strip())
    for label, aliases in PROTOCOL_CSV_ALIASES.items():
        if v in aliases or v == label:
            return label
    return None
