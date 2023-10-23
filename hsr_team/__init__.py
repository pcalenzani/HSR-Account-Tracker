from . import models

def pre_init(cr):
    cr.execute("""CREATE TABLE sr_character_template (id serial, primary key(id));""")
    cr.execute("""CREATE TABLE sr_character (primary key(id)) INHERITS (sr_character_template);""")