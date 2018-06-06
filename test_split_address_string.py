import jakesky

import pytest

def test_split_address_simple():
    parts = ['200 Clarendon St', 'Boston', 'MA', '02116']

    address, city, state, postal_code = jakesky.split_address_string(' '.join(parts))

    assert address == parts[0]
    assert city == parts[1]
    assert state == parts[2]
    assert postal_code == parts[3]


@pytest.mark.xfail
def test_split_address_complex():
    parts = ['1 Elm St', 'Sioux Falls', 'SD', '57101']

    address, city, state, postal_code = jakesky.split_address_string(' '.join(parts))

    assert address == parts[0]
    assert city == parts[1]
    assert state == parts[2]
    assert postal_code == parts[3]


def test_split_address_too_small():
    with pytest.raises(ValueError):
        jakesky.split_address_string('Not An Address')
