from typing import Dict, List, Any
from datetime import datetime

class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.assignment = {}

    def is_consistent(self, var, value):
        # Check all constraints
        for constraint in self.constraints:
            if not constraint(self.assignment, var, value):
                return False
        return True

    def backtrack(self):
        # If everything assigned → done
        if len(self.assignment) == len(self.variables):
            return self.assignment
        
        # Select next unassigned variable
        var = [v for v in self.variables if v not in self.assignment][0]

        for value in self.domains[var]:
            if self.is_consistent(var, value):
                self.assignment[var] = value
                result = self.backtrack()
                if result:
                    return result
                del self.assignment[var]
        return None


def generate_schedule(activities: List[Dict], start_date, end_date, constraints: Dict):

    num_days = (end_date - start_date).days + 1
    max_per_day = constraints.get("max_per_day", 3)

    # Create variables = Day1_Slot1, Day1_Slot2...
    variables = []
    for d in range(num_days):
        for slot in range(max_per_day):
            variables.append(f"Day{d+1}_Slot{slot+1}")

    # Domains = all activities for each slot
    domains = {var: activities.copy() for var in variables}

    # ---------------- Constraints ---------------- #

    def no_duplicate(assignment, var, value):
        return value not in assignment.values()

    def food_after_slot(assignment, var, value):
        if value.get("category") == "food":
            slot_no = int(var.split("_")[1].replace("Slot", ""))
            return slot_no >= constraints.get("food_after_slot", 1)
        return True

    constraints_list = [
        no_duplicate,
        food_after_slot
    ]

    # ---------------- Run CSP ---------------- #
    csp = CSP(variables, domains, constraints_list)
    result = csp.backtrack()

    if not result:
        return {"message": "No valid schedule found for given constraints"}

    # ------------- Format into days ------------- #
    final = {}
    for var, activity in result.items():
        day_key = var.split("_")[0]
        if day_key not in final:
            final[day_key] = []
        final[day_key].append(activity)

    return final
