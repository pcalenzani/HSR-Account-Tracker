from odoo import api, fields, models, tools, Command

# Character Template
class CharacterTemplate(models.Model):
    _name = 'sr.character.template'
    _description = 'Character Template'
    
    avatar = fields.Char("Character Name")
    character_id = fields.Integer('Character ID')
    eidolon_ids = fields.One2many('sr.character.eidolon', 'character_template_id', string='Eidolons')
    warp_ids = fields.One2many('sr.warp', 'character_id', string='Warps')

    # -- Materials --
    general_mat_id = fields.Many2one('sr.item.material', string='General Material')
    general_mat_img = fields.Binary(related='general_mat_id.image', string='General Material Image')
    advanced_mat_id = fields.Many2one('sr.item.material', string='Advanced Material')
    advanced_mat_img = fields.Binary(related='advanced_mat_id.image', string='Advanced Material Image')
    ascension_mat_id = fields.Many2one('sr.item.material', string='Ascension Material')
    ascension_mat_img = fields.Binary(related='ascension_mat_id.image', string='Ascension Material Image')

    # -- Element & Path --
    element_id = fields.Many2one('sr.element', string='Element')
    element_img = fields.Image(related='element_id.image')
    path_id = fields.Many2one('sr.path', string='Path')
    path_img = fields.Image(related='path_id.image')

    _sql_constraints = [
        ('character_key', 'UNIQUE (character_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]

    def browse_sr_id(self, sr_ids=None):
        if not sr_ids:
            sr_ids= ()
        elif sr_ids.__class__ is int:
            sr_ids = (sr_ids,)
        else:
            sr_ids= tuple(sr_ids)

        self.env.cr.execute("""SELECT id FROM sr_character_template WHERE character_id in %s""", [sr_ids])
        ids = tuple(self.env.cr.fetchall())
        return self.__class__(self.env, ids, ids)

    def name_get(self):
        return [(rec.id, f"{rec.avatar} (Template)") for rec in self]
    
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args += ['|', ('avatar',operator,name), ('character_id',operator,name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class Element(models.Model):
    _name = 'sr.element'
    _description = 'Element'
    _inherit = 'sr.image.mixin'

    '''
    ('Wind', 'Wind')
    ('Ice', 'Ice')
    ('Physical', 'Physical')
    ('Fire', 'Fire')
    ('Quantum', 'Quantum')
    ('Lightning', 'Lightning')
    ('Imaginary', 'Imaginary')
    '''
    
    name = fields.Char('Name')
    reference = fields.Char('Internal Ref')
    img_path = fields.Char('Image Path')
    image = fields.Image('Element Image', store=True, compute='_compute_image')

    @api.depends('img_path')
    def _compute_image(self):
        for rec in self:
            rec.image = rec.get_image_data(rec.img_path)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['img_path'] = 'icon/element/%s.png'%(vals['name'])
        return super(Element, self).create(vals_list)
    

class Path(models.Model):
    _name = 'sr.path'
    _description = 'Aeon Path'
    _inherit = 'sr.image.mixin'
    
    '''
    ('Warrior', 'Destruction')
    ('Priest', 'Abundance')
    ('Rogue', 'Hunt')
    ('Mage', 'Erudition')
    ('Shaman', 'Harmony')
    ('Warlock', 'Nihility')
    ('Knight', 'Preservation')
    '''
    
    name = fields.Char("Name")
    reference = fields.Char('Internal Ref')
    img_path = fields.Char('Image Path')
    image = fields.Image('Path Image', store=True, compute='_compute_image')

    @api.depends('img_path')
    def _compute_image(self):
        for rec in self:
            rec.image = rec.get_image_data(rec.img_path)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['img_path'] = 'icon/path/%s.png'%(vals['name'])
        return super(Path, self).create(vals_list)


class Warp(models.Model):
    # Override this model to add character link and compute
    _inherit = 'sr.warp'

    character_id = fields.Many2one('sr.character', store=True, compute='_compute_character_id')

    def _compute_character_id(self):
        for warp in self:
            warp.character_id = self.env['sr.character.template'].search([('character_id','=',warp.item_id)])
