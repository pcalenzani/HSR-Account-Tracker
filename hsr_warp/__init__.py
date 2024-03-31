from . import models

def pre_init(env):
    env.cr.execute("""CREATE TABLE sr_item (id serial, primary key(id));""")
    env.cr.execute("""CREATE TABLE sr_item_material (primary key(id)) INHERITS (sr_item);""")