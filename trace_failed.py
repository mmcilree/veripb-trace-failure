import sys
import re
from constraint import *
from argparse import ArgumentParser

showSlack = False
showNonPropagations = False

if __name__ == "__main__":
    pb_formula = []
    # StackOverflow tells me this magic regex will get rid of the color codes if --useColor is enabled
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    prev_line = ""
    rup_failure = False
    for line in sys.stdin:
        print(line, end="")
        if line.startswith("  ConstraintId ") and not line.startswith("  ConstraintId  -"):
            line = ansi_escape.sub('', line)
            pb_formula.append(Constraint.from_string(line.split(":")[1]))
        
        if line.startswith("Verification failed"):
            if len(prev_line.split("u")) > 1:
                rup_failure = True
                rup_constraint = Constraint.from_string(prev_line.split("u")[1])
                # Put the negated rup constraint at the start so it propagates first
                pb_formula.insert(0, rup_constraint.negate())
        prev_line = line

    if len(pb_formula) == 0 or not rup_failure:
        exit()
    
    
    changed = True
    assignment = {}

    print("=== begin failure trace ===")

    # Run naive unit propagation 
    while(changed):
        changed = False
        contradiction = False
        for c in pb_formula:
            propagated = c.propagate(assignment)
            
            if propagated is None:
                print(c.pb_str())
                print("gives contradiction!")
                contradiction = True
                break

            if len(propagated) > 0:
                changed = True
                print(c.pb_str())
                if showSlack:
                    print("Slack = " + str(c.slack(assignment)))
                print("Propagates: [" + ", ".join(str(l) for l in propagated) + "]")
                print()
                for l in propagated:
                    assignment[l.var] = 0 if l.negated else 1
            elif showNonPropagations:
                print(c.pb_str())
                if showSlack:
                    print("Slack = " + str(c.slack(assignment)))
                print("No propagation\n")
        
        if contradiction:
            break

    if not contradiction:
        print("No further propagation")
    