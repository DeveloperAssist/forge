my sgpa from grades.py doesnt match the university marksheet. i got O in a 4 credit subject and B in a 2 credit lab,
marksheet says 8.67 but the script says 8.0. i think it just averages the grade points??
it should be credit weighted: sum(points x credits) / sum(credits), rounded to 2 decimals. 0-credit audit courses
should not change the answer, F still counts (0 points with its credits). cgpa over semesters works the same way on all subjects together.
