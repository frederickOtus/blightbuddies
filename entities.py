import esper
from dataclasses import dataclass

@dataclass
class Owner:
    name : str = ""
    external_id : str = ""
    external_type : str = "Slack"

@dataclass
class Egg:
    age : int = 0

class EggProcessor(esper.Processor):
    def process(self):
        for entity, (egg, owner) in self.world.get_components(Egg, Owner):
            egg.age += 1
            print(f"{owner.name}: {egg.age}")
