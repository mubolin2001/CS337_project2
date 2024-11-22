class Ingredient:
    def __init__(self, name, quantity, measurement = None, descriptor = None):
        self.name = name
        self.quantity = quantity
        self.measurement = measurement
        self.descriptor = descriptor

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "measurement": self.measurement,
            "descriptor": self.descriptor
        }

class Method:
    def __init__(self, primary_method, other_method = None):
        self.primary_method = primary_method
        self.other_method = other_method

    def to_dict(self):
        return {
            "primary_method": self.primary_method,
            "other_method": self.other_method
        }

class Step:
    def __init__(self, text, previous, next):
        self.text = text
        self.previous = previous
        self.next = next
        self.founding_list = None
    
    def to_dict(self, seen=None):
        if seen is None:
            seen = set()

        if self in seen:
            return {"text": self.text, "previous": None, "next": None}

        seen.add(self)

        return {
            "text": self.text,
            "previous": self.previous.to_dict(seen) if self.previous else None,
            "next": self.next.to_dict(seen) if self.next else None
        }

class Recipe:
    def __init__(self, title, ingredients: list[Ingredient], tools, method, Steps: list[Step]):
        self.title = title
        self.ingredients = ingredients
        self.tools = tools
        self.current_step = Steps[0]
        self.method = method
        self.steps = Steps

    def to_dict(self):
        return {
            "title": self.title,
            "ingredients": [ingredient.to_dict() for ingredient in self.ingredients],
            "tools": self.tools,
            "method": self.method.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "current_step": 0
        }