from uuid import UUID, uuid4

from bank_agent.models import Bank


def sample_bank(
    uuid: UUID = None,
    name: str = "testname",
    token: str = "testtoken",
    url: str = "http://test_url/",
) -> Bank:
    """Create a sample bank"""
    if not uuid:
        uuid = uuid4()
    return Bank.objects.create(name=name, uuid=uuid, token=token, url=url)
