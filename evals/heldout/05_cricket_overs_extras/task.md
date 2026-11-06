gully cricket scorer app bug: overs count goes up on extras. after "1", "wd", "2" it shows 0.3 overs, should be 0.2.
how we write balls: "0".."6" runs, "W" wicket, "wd" wide, "nb" no ball, and extras with runs off them like "wd+1" or "nb+4".
wides and no balls (with or without +runs) are NOT legal balls so the over must not move on them. everything else is a legal ball.
run rate uses legal balls too. pls fix in score.py
