# veripb-trace-failure
Given a VeriPB proof trace that ends with a RUP failure, print all the unit propagations that result from the display anything that propagated under the negation of the failing RUP constraint. 

Usage: pipe veripb with the trace option enabled, e.g.
```
veripb --trace --useColor test/disconnected.opb test/disconnected.veripb | python3 trace_failed.py
```
Note that this code has not been rigorously tested and doesn't do anything clever with the propagations, thus the output might be wrong or hard to interpret.
