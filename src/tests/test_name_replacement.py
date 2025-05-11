import json
import pytest
from tempfile import NamedTemporaryFile
from src.utils.naming_json_utils import load_name_config, get_name_by_mail

# Beispiel-Datenstruktur
NAME_CONFIG = {
    "Silas Hage": [
        "silas.hage@protonmail.com"
    ],
    "Malte Borgmann": [
        "malte.borgmann@protonmail.com",
        "malte@borgmann.tech",
        "borgmann25@itu.edu.tr"
    ],
    "Jakob Paul Fischer": [
        "jako.fischer@ostfalia.de",
        "117381184+jakobfsr@users.noreply.github.com"
    ]
}

def test_load_name_config():
    with NamedTemporaryFile(mode="w+", delete=False) as tmp:
        json.dump(NAME_CONFIG, tmp)
        tmp.seek(0)
        config = load_name_config(tmp.name)
        assert config == NAME_CONFIG

@pytest.mark.parametrize("email,expected_name", [
    ("silas.hage@protonmail.com", "Silas Hage"),
    ("malte@borgmann.tech", "Malte Borgmann"),
    ("117381184+jakobfsr@users.noreply.github.com", "Jakob Paul Fischer"),
    ("unknown@example.com", None),
])
def test_get_name_by_mail(email, expected_name):
    result = get_name_by_mail(email, NAME_CONFIG)
    assert result == expected_name
