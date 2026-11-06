need a new function in placements.py for our T&P cell portal:

`eligible_companies(student, companies)` -> list of company names the student can apply to.

rules (from the placement policy pdf):
- student.cgpa must be >= company.min_cgpa
- student.backlogs (active backlogs) must be <= company.max_backlogs
- company.branches is a list of branch codes like ["CSE", "IT"]; empty list means all branches allowed
- if the student is already placed (student.placed_lpa is not None), they can only apply where company.package_lpa is
  at least 1.5 times their current package (the "dream offer" rule). not placed = no limit.
- order: highest package first, if same package then name A-Z

dont change the dataclasses pls, other code uses them
