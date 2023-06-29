import pytest

from oaipmh.add_handles import extract_from_url


@pytest.mark.parametrize(
    ('fcrepo_path'),
    [
        'dc/2021/2/27/fb/47/4e/27fb474e-4fef-43f7-bb57-18577a6ab944',
        'dc/2021/2/8a/7f/e2/ef/8a7fe2ef-fdb1-4c2c-8199-6fe276d908e4',
        'dc/2021/2/a3/53/da/54/a353da54-0401-41a1-bd40-0264d0d40661',
        'dc/2021/2/06/db/6b/11/06db6b11-3be3-4710-9bbf-ba3a751dd633',
        'dc/2021/2/78/f8/fb/9b/78f8fb9b-ce67-403f-9226-a22dda4f3085',
        'dc/2021/2/ed/15/1c/12/ed151c12-2615-4dc1-8691-510b64d17ea0',
        'dc/2021/2/a8/90/3c/d8/a8903cd8-8b85-4e29-9e99-d659e2627b53',
        'dc/2021/2/ff/24/18/ba/ff2418ba-8ea1-4eb1-a177-a56f626e290f',
        'dc/2021/2/f4/e7/83/28/f4e78328-265d-4708-a5dd-5da3385b0055',
        'dc/2021/2/4e/27/03/ac/4e2703ac-2c8e-4982-bade-94c88e213b51',
        'dc/2021/2/c8/9f/ae/bb/c89faebb-2709-4e8d-9975-e90510d39a98'
    ]
)
def test_extract(fcrepo_path):
    correct_relpath = 'dc/2021/2'
    correct_uuid = fcrepo_path.split('/')[-1]

    relpath, uuid = extract_from_url(fcrepo_path)
    assert relpath == correct_relpath
    assert uuid == correct_uuid
