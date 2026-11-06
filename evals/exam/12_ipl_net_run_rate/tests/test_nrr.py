"""How net_run_rate(matches, team) and the new table() must work.

* NRR = (total runs scored / total overs faced) - (total runs conceded / total overs bowled),
  added up over ALL the team's matches (not an average of per-match NRRs).
* Overs are in cricket notation: "18.3" = 18 overs + 3 balls = 18.5 overs.
* If a side is all out, its innings counts as the full 20 overs, whatever the overs say.
* No-result matches (winner None) are left out of NRR.
* A team with no counted matches has NRR 0.0.
* The result is rounded to 3 decimals.
* table(matches) returns rows (team, points, nrr), most points first, ties broken by higher NRR,
  then by team name.
"""
from points_table import net_run_rate, table


def m(t1, r1, o1, t2, r2, o2, winner, out1=False, out2=False):
    return {"team1": t1, "team2": t2, "team1_runs": r1, "team1_overs": o1, "team1_all_out": out1,
            "team2_runs": r2, "team2_overs": o2, "team2_all_out": out2, "winner": winner}


def test_simple():
    ms = [m("CSK", 180, "20.0", "MI", 160, "20.0", "CSK")]
    assert net_run_rate(ms, "CSK") == 1.0
    assert net_run_rate(ms, "MI") == -1.0


def test_overs_notation():
    ms = [m("CSK", 150, "20.0", "MI", 151, "18.3", "MI")]
    assert net_run_rate(ms, "MI") == 0.662
    assert net_run_rate(ms, "CSK") == -0.662


def test_all_out_counts_full_overs():
    ms = [m("MI", 140, "17.2", "CSK", 141, "15.0", "CSK", out1=True)]
    assert net_run_rate(ms, "CSK") == 2.4
    assert net_run_rate(ms, "MI") == -2.4


def test_aggregate_not_average():
    ms = [m("CSK", 200, "20.0", "RR", 150, "20.0", "CSK"),
          m("GT", 180, "20.0", "CSK", 181, "15.0", "CSK")]
    assert net_run_rate(ms, "CSK") == 2.636


def test_no_result_skipped():
    ms = [m("KKR", 50, "6.0", "SRH", 0, "0.0", None)]
    assert net_run_rate(ms, "KKR") == 0.0


def test_table_tiebreak():
    ms = [m("CSK", 200, "20.0", "MI", 120, "20.0", "CSK"),
          m("MI", 160, "20.0", "RR", 150, "20.0", "MI"),
          m("RR", 170, "20.0", "CSK", 165, "20.0", "RR")]
    assert table(ms) == [("CSK", 2, 1.875), ("RR", 2, -0.125), ("MI", 2, -1.75)]
