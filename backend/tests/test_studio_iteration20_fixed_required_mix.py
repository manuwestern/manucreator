"""Iteration 20 backend retest: protected own-template fixed-text mutation rejection."""

from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

import requests

from test_studio_iteration18_templates_decorations import (
    BASE_URL,
    _create_template,
    _publish_template,
    _text_element,
)

pytest_plugins = ['test_studio_iteration18_templates_decorations']


# Module coverage: protected template keeps fixed text immutable while customer field remains editable
def test_fixed_text_mutation_rejected_with_required_customer_text(admin_session, created_ids):
    fixed_id = f"txt-fixed-{uuid4().hex[:6]}"
    customer_id = f"txt-customer-{uuid4().hex[:6]}"

    fixed_text = _text_element(
        id=fixed_id,
        text="FESTER TEXT",
        template_field=None,
        field_label=None,
        template_slot=None,
        field_required=False,
        x=260,
        y=300,
        w=280,
        h=72,
    )
    required_customer = _text_element(
        id=customer_id,
        text="Mia",
        template_field=f"field-{uuid4().hex[:6]}",
        field_label="Vorname",
        template_slot={"x": 240, "y": 390, "w": 320, "h": 120},
        field_required=True,
        field_max_length=24,
        x=290,
        y=420,
        w=220,
        h=60,
    )

    template = _create_template(
        admin_session,
        created_ids,
        "holzscheibe",
        elements=[required_customer, fixed_text],
        allow_free_edit=False,
        name=f"TEST_I20_FIXED_REQUIRED_{uuid4().hex[:6]}",
    )
    published = _publish_template(admin_session, created_ids, template["id"], template["revision"])

    guest_token = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20).json()["token"]
    headers = {"Authorization": f"Bearer {guest_token}"}

    applied = requests.post(
        f"{BASE_URL}/api/studio/article-templates/{template['id']}/apply",
        headers=headers,
        timeout=25,
    )
    assert applied.status_code == 200, applied.text
    design = applied.json()

    editable_field_count = sum(1 for element in design["elements"] if element.get("template_field"))
    assert editable_field_count == 1

    valid_personalization = deepcopy(design)
    for element in valid_personalization["elements"]:
        if element.get("template_field") == required_customer["template_field"]:
            element["text"] = "Nora"

    valid_save = requests.post(
        f"{BASE_URL}/api/studio/drafts",
        headers=headers,
        json=valid_personalization,
        timeout=35,
    )
    assert valid_save.status_code == 200, valid_save.text

    forged = deepcopy(valid_personalization)
    for element in forged["elements"]:
        if element["kind"] == "text" and not element.get("template_field"):
            element["text"] = "HACKED"

    forged_save = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=forged, timeout=35)
    assert forged_save.status_code == 422, forged_save.text
    assert "Feste Inhalte" in forged_save.text or "verändert" in forged_save.text

    archive = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{template['id']}/archive",
        timeout=25,
    )
    assert archive.status_code == 200, archive.text
    assert archive.json()["archived"] is True
    assert archive.json()["published_revision_id"] == published["published_revision_id"]
