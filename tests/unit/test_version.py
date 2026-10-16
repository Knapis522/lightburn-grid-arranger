"""Verze aplikace: jediný zdroj, SemVer pro GUI, ZIP, tag a release notes (spec. kap. 30.3)."""

import pytest

from grid_arranger.version import __version__, display_version


@pytest.mark.parametrize("pep440, semver", [
    ("0.1.0a1", "0.1.0-alpha.1"), ("0.1.0b2", "0.1.0-beta.2"), ("1.0.0rc1", "1.0.0-rc.1"),
    ("1.0.0", "1.0.0"), ("0.1.0.dev0", "0.1.0-dev"), ("1.1.1", "1.1.1"),
])
def test_display_version(pep440, semver):
    assert display_version(pep440) == semver


def test_invalid_version_rejected():
    with pytest.raises(ValueError):
        display_version("1.0")


def test_current_version_is_first_alpha():
    assert display_version(__version__) == "0.1.0-alpha.1"
