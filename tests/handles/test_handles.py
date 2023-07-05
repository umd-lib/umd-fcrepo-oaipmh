import pytest

from oaipmh.add_handles import extract_from_path


@pytest.mark.parametrize(
    ('fcrepo_path', 'expected_relpath', 'expected_uuid'),
    [
        (
            'dc/2021/2/27/fb/47/4e/27fb474e-4fef-43f7-bb57-18577a6ab944',
            'dc/2021/2',
            '27fb474e-4fef-43f7-bb57-18577a6ab944',
        ),
        (
            'pcdm/8a/7f/e2/ef/8a7fe2ef-fdb1-4c2c-8199-6fe276d908e4',
            'pcdm',
            '8a7fe2ef-fdb1-4c2c-8199-6fe276d908e4',
        ),
    ]
)
def test_extract(fcrepo_path, expected_relpath, expected_uuid):
    relpath, uuid = extract_from_path(fcrepo_path)
    assert relpath == expected_relpath
    assert uuid == expected_uuid


def test_extract_failure():
    with pytest.raises(RuntimeError):
        extract_from_path('/foo/bar/no/pairtree')
