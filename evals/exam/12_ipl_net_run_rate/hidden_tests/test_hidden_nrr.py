from fractions import Fraction

import pytest

import points_table as pt


def m(t1, r1, o1, t2, r2, o2, winner, out1=False, out2=False):
    return {"team1": t1, "team2": t2, "team1_runs": r1, "team1_overs": o1, "team1_all_out": out1,
            "team2_runs": r2, "team2_overs": o2, "team2_all_out": out2, "winner": winner}


SEASON = [
    m("CSK", 187, "20.0", "MI", 175, "19.2", "CSK", out2=True),
    m("RR", 142, "20.0", "CSK", 143, "17.5", "CSK"),
    m("MI", 210, "20.0", "RR", 211, "19.5", "RR"),
    m("GT", 99, "14.3", "MI", 100, "11.1", "MI", out1=True),
    m("GT", 160, "20.0", "CSK", 30, "3.2", None),
    m("RR", 155, "20.0", "GT", 150, "20.0", "RR"),
    m("GT", 205, "20.0", "CSK", 190, "18.4", "GT", out2=True),
]


def ref_nrr(matches, team):
    def overs(s, all_out):
        if all_out:
            return Fraction(20)
        o, _, b = s.partition(".")
        return Fraction(int(o)) + Fraction(int(b or 0), 6)

    rs = of = rc = ob = Fraction(0)
    for x in matches:
        if x["winner"] is None or team not in (x["team1"], x["team2"]):
            continue
        us, them = ("team1", "team2") if x["team1"] == team else ("team2", "team1")
        rs += x[us + "_runs"]
        of += overs(x[us + "_overs"], x[us + "_all_out"])
        rc += x[them + "_runs"]
        ob += overs(x[them + "_overs"], x[them + "_all_out"])
    if not of or not ob:
        return 0.0
    return float(rs / of - rc / ob)


@pytest.mark.parametrize("team", ["CSK", "MI", "RR", "GT"])
def test_season_nrr(team):
    got = pt.net_run_rate(SEASON, team)
    assert got == pytest.approx(ref_nrr(SEASON, team), abs=6e-4)
    assert got == round(got, 3)


def test_season_table():
    rows = pt.table(SEASON)
    assert [r[0] for r in rows] == ["CSK", "RR", "GT", "MI"]
    assert [r[1] for r in rows] == [5, 4, 3, 2]
    for team, _, nrr in rows:
        assert nrr == pytest.approx(ref_nrr(SEASON, team), abs=6e-4)


def test_tie_on_points_uses_nrr():
    ms = [
        m("KKR", 220, "20.0", "SRH", 130, "16.1", "KKR", out2=True),
        m("SRH", 181, "18.2", "PBKS", 180, "20.0", "SRH"),
        m("PBKS", 200, "20.0", "KKR", 120, "20.0", "PBKS"),
        m("DC", 100, "20.0", "LSG", 101, "9.0", "LSG"),
        m("LSG", 90, "20.0", "DC", 91, "19.5", "DC"),
    ]
    names = [r[0] for r in pt.table(ms)]
    expected = sorted(["KKR", "SRH", "PBKS", "DC", "LSG"], key=lambda t: (-ref_nrr(ms, t), t))
    assert names == expected


def test_team_without_matches():
    assert pt.net_run_rate(SEASON, "DC") == 0.0
