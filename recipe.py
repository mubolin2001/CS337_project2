
class Ingredient:
    def __init__(self, name, quantity, measurement = None, descriptor = None):
        self.name = name
        self.quantity = quantity
        self.measurement = measurement
        self.descriptor = descriptor


class Method:
    def __init__(self, primary_method, other_method = None):
        self.primary_method = primary_method
        self.other_method = other_method


class Step:
    def __init__(self, text, previous, next):
        self.text = text
        self.previous = previous
        self.next = next
        self.founding_list = None


class Recipe:
    def __init__(self, ingredients: list[Ingredient], tools, method, Steps: list[Step]):
        self.ingredients = ingredients
        self.tools = tools
        self.current_step = Steps[0]
        self.method = method
        self.steps = Steps