def test_equality2():
    assert (1,2,3) == (1,2,3)

def test_difference2():
    assert (1,2,3) != (1,1,3)


def test_error2():
    assert (1,2,3) == (1,1,3)