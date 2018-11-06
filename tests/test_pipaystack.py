import pytest
from pipaystack import get_version
from requests import Session


def test_version():
    assert get_version() == '0.1.0'
