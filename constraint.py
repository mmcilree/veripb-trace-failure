class ParseError(Exception):
    pass

class Literal:
    def __init__(self, var, negated):
        self.var = var
        self.negated = negated

    def negate(self):
        return Literal(self.var, not self.negated)

    def __str__(self):
        return ("~" if self.negated else "") + self.var

class Constraint:
    def __init__(self, coeffs, lits, lower_bound, normalise=True):
        assert(len(coeffs) == len(lits))
        self.lits = lits
        self.coeffs = coeffs
        self.lower_bound = lower_bound
        if normalise:
            self.normalise()

    @classmethod
    def from_string(self, line):
        tokens = line.split()
        idx = 0
        coeffs = []
        lits = []

        while(tokens[idx] != ">="):
            if idx >= len(tokens):
                raise ParseError()
            coeffs.append(int(tokens[idx]))
            if tokens[idx + 1][0] == "~":
                lits.append(Literal(tokens[idx + 1][1:], True))
            else:
                lits.append(Literal(tokens[idx + 1], False))
            idx += 2
        
        lower_bound = int(tokens[idx + 1])
        return Constraint(coeffs, lits, lower_bound)

    def normalise(self):
        lits = self.lits
        coeffs = self.coeffs
        lower_bound = self.lower_bound
        self.lits = []
        self.coeffs = []
        self.lower_bound = lower_bound

        for i in range(len(lits)):
            if coeffs[i] >= 0:
                self.lits.append(lits[i])
                self.coeffs.append(coeffs[i])
            else:
                self.coeffs.append(-coeffs[i])
                self.lits.append(lits[i].negate())
                self.lower_bound += -coeffs[i]
    
    def negate(self):
        return Constraint([-a for a in self.coeffs], self.lits, -self.lower_bound + 1)

    def in_normal_form(self):
        return all([coeff >= 0 for coeff in self.coeffs])

    def pb_str(self):
        pb = ""
        for i in range(len(self.lits)):
            pb += str(self.coeffs[i]) + " " + str(self.lits[i]) + " "
        pb += ">= " + str(self.lower_bound) + ";"
        return pb

    def slack(self, assignment):
        if(not self.in_normal_form()):
            self.normalise()

        lh_sum = 0
        for i in range(len(self.lits)):
            add_to_sum = not self.lits[i].var in assignment \
                or (self.lits[i].negated and assignment.get(self.lits[i].var) == 0) \
                or (not self.lits[i].negated and assignment.get(self.lits[i].var) == 1)

            if(add_to_sum):
                lh_sum += self.coeffs[i]
        
        return lh_sum - self.lower_bound

    def propagate(self, assignment):
        propagated = []
        slack = self.slack(assignment)
        if slack < 0:
            return None

        for i in range(len(self.lits)):
            if self.coeffs[i] > slack and not self.lits[i].var in assignment:
                propagated.append(self.lits[i])
        
        return propagated
            
