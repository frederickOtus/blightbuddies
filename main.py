from world import PersistentWorld
from entities import *
import time, sys

if __name__ == "__main__":
    world = PersistentWorld()
    world.interval = 3
    world.path = "/home/envtest/coding/blightbuddies/instance"

    if not world.load():
        print("No save loaded, creating new")
        world.create_entity(Owner(name="Peter"), Egg())
    else:
        print("Save loaded")

    world.add_processor(EggProcessor())
    while True:
        try:
            world.process()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Saving, closing")
            world.save()
            sys.exit()
