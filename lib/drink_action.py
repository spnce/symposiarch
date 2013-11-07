class DrinkAction:

    def __init__(self, drinker, measurements):
        self.drinker = drinker
        self.measurements = measurements

    def get(self):
<<<<<<< HEAD
    	hours = 1
    	gender_constant = 0.58 if self.drinker.gender else 0.49
    	adjusted_weight = self.drinker.weight * 0.453592 * gender_constant
    	metabolized = (0.01 + 0.005 * self.drinker.tolerance) * hours
    	drinks = (0.138 - measurements['current_bac']) * adjusted_weight / (0.806 * 1.2) - metabolized
    	return drinks
    	
=======
        pass
>>>>>>> 9ae9b410a393c9a2e81e4441ca91cd01c6123ce9
