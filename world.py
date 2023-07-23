import esper
import json
import os
import dataclasses
import entities
from typing import Dict as _Dict

class PersistentWorld(esper.World):

    interval : int = 100
    path : str = ""
    save_name : str = "persistent"
    number_of_backups : int = 5
    tick : int = 0
    
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
            print(export)
            f.write(json.dumps(export, indent=2))

    def save(self):
        """
        Cycles backups saves and save new file.
        """

        # Cycle old backups:
        base_path = f"{self.path}/{self.save_name}.json"
        for i in range(self.number_of_backups - 1, 0, -1):
            old_name = base_path + ".bak" + str(i)
            new_name = base_path + ".bak" + str(i+1)
            if os.path.isfile(old_name):
                os.replace(old_name, new_name)

        # Handle current save.
        if os.path.isfile(base_path):
            os.replace(base_path, base_path + ".bak1")

        self.write_save(base_path)

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

        base_path = f"{self.path}/{self.save_name}.json"
        if not os.path.isfile(base_path):
            return False

        data = {}
        with open(base_path) as f:
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
