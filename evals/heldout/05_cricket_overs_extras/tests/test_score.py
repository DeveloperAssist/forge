from score import overs_text


def test_wide_not_counted():
    assert overs_text(["1", "wd", "2"]) == "0.2"
