from __future__ import annotations

import json
from pathlib import Path

import pytest

from pubfig.figma import load_figma_bundle_payload


def _write_bundle(path: Path, svg_text: str) -> Path:
    payload = {
        "bundle_type": "pubfig_figma_bundle",
        "schema_version": 1,
        "figure_id": "figure-01",
        "panels": [
            {
                "panel_id": "a",
                "svg": svg_text,
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def test_bundle_accepts_minimal_inline_svg(tmp_path) -> None:
    bundle_path = _write_bundle(
        tmp_path / "ok.pubfig-figma.json",
        '<svg xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="clip-1" /></defs><g clip-path="url(#clip-1)"><rect width="12" height="8" /></g></svg>',
    )

    payload = load_figma_bundle_payload(bundle_path)

    assert payload["figure_id"] == "figure-01"
    assert payload["panels"][0]["panel_id"] == "a"


@pytest.mark.parametrize(
    ("svg_text", "message"),
    [
        ('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', "script tag"),
        ('<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"><rect width="12" height="8" /></svg>', "event attribute"),
        (
            '<svg xmlns="http://www.w3.org/2000/svg"><foreignObject width="10" height="10"><div xmlns="http://www.w3.org/1999/xhtml">x</div></foreignObject></svg>',
            "foreignObject",
        ),
        ('<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.com/panel.png" /></svg>', "external href"),
        ('<svg xmlns="http://www.w3.org/2000/svg"><image xlink:href="file:///tmp/panel.png" xmlns:xlink="http://www.w3.org/1999/xlink" /></svg>', "external href"),
    ],
)
def test_bundle_rejects_unsafe_svg_content(tmp_path, svg_text: str, message: str) -> None:
    bundle_path = _write_bundle(tmp_path / "bad.pubfig-figma.json", svg_text)

    with pytest.raises(ValueError, match=message):
        load_figma_bundle_payload(bundle_path)
