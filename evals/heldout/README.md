# Held-out exam (12 tasks)

Written blind on 2026-11-06 by a separate agent; run once.

Check validity: `uv run python evals/check_exam.py --set heldout`

| Task | Kind | What it tests |
|---|---|---|
| 01_metro_fare_slabs | bug fix | `<` vs `<=` at every fare-slab edge; visible test only checks 5 km, hidden checks all edges + card/day totals |
| 02_fest_group_discount | bug fix | group discount uses `== 4` / `== 10` instead of ranges; visible test is a group of 5, hidden checks every size |
| 03_pincode_check | bug fix | PIN validation special-cases "000000"; the real rule is first digit 1-9 and ASCII digits only (no Unicode digits) |
| 04_cgpa_credit_weight | bug fix | SGPA/CGPA is a plain mean; must be credit-weighted, 0-credit audit courses ignored, F counted |
| 05_cricket_overs_extras | bug fix | overs count every delivery; wides and no-balls (incl. "wd+1", "nb+4") are not legal balls; run rate follows |
| 06_train_berth_type | bug fix | seat range check is 0..size-1; must be 1..size for every coach class (SL, 3A, 2A) |
| 07_fest_registration_keyerror | crash (traceback) | KeyError 'phone' on optional form fields; a second hidden KeyError on optional 'team' (solo = own team) |
| 08_canteen_token_crash | crash (traceback) | IndexError on an empty queue; a second hidden ZeroDivisionError in avg_wait when no order is ready |
| 09_placement_eligibility | feature | new `eligible_companies`: CGPA, backlogs, branch list, 1.5x dream-offer rule, ordering by package then name |
| 10_upi_split_equal | feature | new `split_equal`: paise sum exactly, leftovers to earliest names, order kept, ValueError on bad input |
| 11_rename_hostel_fee | multi-file rename | `calc(n)` -> `hostel_fee(months)` across fees.py, receipt.py, defaulters.py and the test; old name must be gone |
| 12_explain_batting_average | explain only (no change) | student's test is wrong (average = runs / dismissals); agent must explain and change nothing; see grading.md |
