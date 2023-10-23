from . import models

def pre_init(cr):
    cr.execute("""CREATE TABLE sr_item (id serial, primary key(id));""")
    cr.execute("""CREATE TABLE sr_character (primary key(id)) INHERITS (sr_item);""")
    cr.execute("""CREATE TABLE sr_light_cone (primary key(id)) INHERITS (sr_item);""")