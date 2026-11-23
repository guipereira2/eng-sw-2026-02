import pytest

from ciclobox.shared.database import ping_database


@pytest.mark.integration
def test_connects_to_real_postgres():
    ping_database()
