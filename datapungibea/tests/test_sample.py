# content of test_sample.py
def test_answer(cmdopt):
    if cmdopt == "type1":
        print("first")
        assert 0  # to see what was printed
    elif cmdopt == "type2":
        print("second")
        assert 1  # to see what was printed