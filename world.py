import esper
import json
import os
import dataclasses
import entities
from entities import *
from typing import Dict as _Dict, Optional
from pathlib import Path

class PersistentWorld(esper.World):

    interval : int = 100
    path :  Path
    save_name : str = "persistent"
    number_of_backups : int = 5
    tick : int = 0

    def __init__(self, tick_rate: int = 3600, save_path = None):

        self.interval = tick_rate

        # Ensure path exists.
        if save_path is None:
            save_path = Path(__file__).parent.joinpath('instance')
        else:
            save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        self.path = save_path

        super().__init__()
    
    def write_save(self, filepath):
        """
        Serialize the Entities to JSON and write to disk.

        Iterate through every entity, and create an export of of the atrributes of it's components.
        """

        export : _Dict[str, _Any] = {}
        export['next_entity_id'] = self._next_entity_id
        export['tick'] = self.tick
        export['entities'] = []

        for id, components in self._entities.items():
            component_exports = []
            for component_class, component in components.items():
                component_exports.append({
                    'type': component_class.__name__,
                    'attributes': dataclasses.asdict(component),
                })

            entity_export : _Dict[str, _Any] = {
                'id' : id,
                'components': component_exports,
            }

            export['entities'].append(entity_export)

        with open(filepath, 'w') as f:
            f.write(json.dumps(export, indent=2))

    def save(self):
        """
        Cycles backups saves and save new file.
        """

        # Cycle old backups:
        base_name = f"{self.save_name}.json"
        for i in range(self.number_of_backups - 1, 0, -1):
            old_name = self.path.joinpath(base_name + ".bak" + str(i))
            new_name = self.path.joinpath(base_name + ".bak" + str(i+1))
            if old_name.is_file():
                os.replace(str(old_name), str(new_name))

        # Handle current save.
        current_save = self.path.joinpath(base_name)
        target_save = self.path.joinpath(base_name + '.bak1')
        if current_save.is_file():
            os.replace(str(current_save), str(target_save))

        self.write_save(current_save)

    def process(self, *args, **kwargs):
        res = super().process(*args, **kwargs)
        self.tick += 1
        if self.tick % self.interval == 0:
            self.save()
            print("saved")

    def load(self):
        """
        Attempts to load world from file.
        Returns true if a save file was found a loaded

        Throws error if _next_entity_id != 0
            OR if _components is not empty
            OR if _entities is not empty
        """
        if (self._next_entity_id != 0
            or len(self._components) != 0
            or len(self._entities) != 0):
            raise Exception("World has already changed state")

        current_save = self.path.joinpath(f"{self.save_name}.json")
        if not current_save.is_file():
            return False

        data = {}
        with current_save.open() as f:
            data = json.loads(f.read())

        self.tick = data['tick']
        self._next_entity_id = data['next_entity_id']
        for entity in data['entities']:
            id = entity['id']
            self._entities[id] = {}

            for component in entity['components']:
                cls = getattr(entities, component['type'])
                if cls not in self._components:
                    self._components[cls] = set()
                inst = cls(**component['attributes'])
                self._components[cls].add(id)
                self._entities[id][cls] = inst
        return True

    def get_players(self) -> [str]:
        players = self.get_component(Owner)
        return [ p.name for (e,p) in players ]

    def create_player(self, name) -> Optional[str]:
        players = self.get_players()
        if name in players:
            return "Player already exists"
        self.create_entity(Owner(name=name), Egg())
