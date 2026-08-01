from syncmark_demo import __version__


def test_package_exposes_public_version() -> None:
    assert __version__ == "0.1.0"
