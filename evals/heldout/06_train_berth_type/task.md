berth.py throws "no such seat" for seat 72 in a sleeper coach but 72 is literally the last berth (side upper). meanwhile it
happily returns something for seat 0 which doesnt exist lol.
seats are numbered from 1 to the coach size: SL and 3A have 72, 2A has 48. anything outside 1..size should raise ValueError,
for every class. the berth pattern itself is right i think
