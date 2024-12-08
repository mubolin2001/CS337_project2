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
    def __init__(self, text, previous = None, next = NotImplemented, ingredients=None, time=None, temperature=None, tool_substitution=None):
        self.text = text
        #self.previous = previous
        #self.next = next
        self.founding_list = None
        self.ingredients = ingredients if ingredients else {}  #Ingredients used in this step
        self.time = time  # Time required for this step, if any
        self.temperature = temperature  # Temperature required for this step, if any
        self.tool_substitution = tool_substitution  # Possible tool substitutions for this step
    
    def to_dict(self, seen=None):
        if seen is None:
            seen = set()

        if self in seen:
            return {"text": self.text, "previous": None, "next": None}

        seen.add(self)

        return {
            "text": self.text,
            #"previous": self.previous.to_dict(seen) if self.previous else None,
            #"next": self.next.to_dict(seen) if self.next else None,
            "ingredients": self.ingredients,
            "time": self.time,
            "temperature": self.temperature
            #"tool_substitution": self.tool_substitution
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
class RecipeTransformer:
    """Class to handle transformations to and from vegetarian recipes."""

    MEAT_TO_VEG_SUBS = {
        "chicken": "tofu",
        "beef": "mushrooms",
        "pork": "tempeh",
        "fish": "jackfruit",
        "shrimp": "king oyster mushrooms",
        "bacon": "smoked tofu",
        "ground meat": "lentils",
        "sausage": "vegetarian sausage",
        "duck": "seitan",
        "lamb": "eggplant",
        "meat": "vegetables"
    }

    VEG_TO_MEAT_SUBS = {
        "tofu": "chicken",
        "mushrooms": "beef",
        "tempeh": "pork",
        "jackfruit": "fish",
        "lentils": "ground meat",
        "smoked tofu": "bacon",
        "vegetarian sausage": "sausage",
        "seitan": "duck",
        "eggplant": "lamb"
    }

    def transform_to_vegetarian(self, ingredients: list[Ingredient], steps: list[Step]) -> tuple:
        """Transform non-vegetarian ingredients and update steps."""
        for ingredient in ingredients:
            for meat, substitute in self.MEAT_TO_VEG_SUBS.items():
                if meat in ingredient.name.lower():
                    ingredient.name = ingredient.name.replace(meat, substitute)
                    ingredient.descriptor = "vegetarian"
                    # Update the steps to replace the meat with the substitute
                    self._update_steps(steps, meat, substitute)
        return ingredients, steps

    def transform_to_non_vegetarian(self, ingredients: list[Ingredient], steps: list[Step]) -> tuple:
        """Transform vegetarian ingredients and update steps."""
        for ingredient in ingredients:
            for veg, substitute in self.VEG_TO_MEAT_SUBS.items():
                if veg in ingredient.name.lower():
                    ingredient.name = ingredient.name.replace(veg, substitute)
                    ingredient.descriptor = "non-vegetarian"
                    # Update the steps to replace the vegetarian ingredient with the substitute
                    self._update_steps(steps, veg, substitute)
        return ingredients, steps

    def _update_steps(self, steps: list[Step], old_term: str, new_term: str):
        """Helper method to replace terms in step descriptions."""
        for step in steps:
            if old_term in step.text.lower():
                step.text = step.text.replace(old_term, new_term)
