import pytest

import score


@pytest.mark.parametrize(
    "balls,overs",
    [
        (["1", "wd", "2"], "0.2"),
        (["1", "nb", "2"], "0.2"),
        (["nb+4", "wd+1", "0"], "0.1"),
        (["1", "2", "3", "4", "6", "W"], "1.0"),
        (["1", "2", "wd", "3", "4", "nb", "6", "W", "0"], "1.1"),
        (["wd", "wd", "wd"], "0.0"),
        (["0"] * 13, "2.1"),
    ],
)
def test_overs(balls, overs):
    assert score.overs_text(balls) == overs


def test_run_rate_uses_legal_balls():
    balls = ["4", "wd", "nb+2", "6", "1", "1", "0", "W"]  # 6 legal, 12 + 1 + 3 = 16 runs
    assert score.run_rate(balls) == 16.0


def test_scoreline():
    assert score.scoreline(["4", "wd+4", "W", "nb"]) == "10/1 in 0.2 ov"
