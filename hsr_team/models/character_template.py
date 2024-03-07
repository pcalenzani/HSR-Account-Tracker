from odoo import api, fields, models, tools, Command

# Character Template
class CharacterTemplate(models.Model):
    _name = 'sr.character.template'
    _description = 'Character Template'
    _inherit = 'sr.image.mixin'
    
    avatar = fields.Char("Character Name")
    character_id = fields.Integer('Character ID')
    eidolon_ids = fields.One2many('sr.character.eidolon', 'character_template_id', string='Eidolons')
    warp_ids = fields.One2many('sr.warp', 'character_id', string='Warps')

    # -- Materials --
    general_mat_id = fields.Many2one('sr.item.material', string='General Material')
    general_mat_img_id = fields.Many2one(related='general_mat_id.img_id', string='General Material Image')
    advanced_mat_id = fields.Many2one('sr.item.material', string='Advanced Material')
    advanced_mat_img_id = fields.Many2one(related='advanced_mat_id.img_id', string='Advanced Material Image')
    ascension_mat_id = fields.Many2one('sr.item.material', string='Ascension Material')
    ascension_mat_img_id = fields.Many2one(related='ascension_mat_id.img_id', string='Ascension Material Image')

    # -- Element & Path --
    element_id = fields.Many2one('sr.element', string='Element')
    element_img_id = fields.Many2one(related='element_id.img_id')
    path_id = fields.Many2one('sr.path', string='Path')
    path_img_id = fields.Many2one(related='path_id.img_id')

    # -- Character Images --
    portrait_img_id = fields.Many2one('ir.attachment', string='Portrait Image',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','portrait_img_id')]")
    preview_img_id = fields.Many2one('ir.attachment', string='Preview Image',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','preview_img_id')]")
    icon_img_id = fields.Many2one('ir.attachment', string='Icon Image',
                        domain="[('res_model','=','sr.character.template'),('res_field','=','icon_img_id')]")

    _sql_constraints = [
        ('character_key', 'UNIQUE (character_id)',  'Duplicate character deteced. Item ID must be unique.')
    ]

    @api.depends('avatar')
    def _compute_display_name(self):
        # Compute name, example: Dan (Template)
        return [(rec.id, f"{rec.avatar} (Template)") for rec in self]
    
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args += ['|', ('avatar',operator,name), ('character_id',operator,name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

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
    
    @api.model_create_multi
    def create(self, vals_list):
        # On creation, look up images with corresponding character id
        for vals in vals_list:
            if 'character_id' in vals:
                # Generate image attachments for each image type
                portrait_img_path = '/hsr_warp/static/image/character_portrait/'
                vals['portrait_img_id'] = self.generate_image(portrait_img_path,
                                                              vals['character_id'],
                                                              field='portrait_img_id').id
                preview_img_path = '/hsr_warp/static/image/character_preview/'
                vals['preview_img_id'] = self.generate_image(preview_img_path,
                                                             vals['character_id'],
                                                             field='preview_img_id').id
                icon_img_path = '/hsr_warp/static/icon/character/'
                vals['icon_img_id'] = self.generate_image(icon_img_path,
                                                          vals['character_id'],
                                                          field='icon_img_id').id
        return super(CharacterTemplate, self).create(vals_list)
    
    # WINDOW ACTIONS
    def action_element(self):
        return {
            'name': 'Character Element',
            'type': 'ir.actions.act_window',
            'res_model': 'sr.element',
            'view_mode': 'form',
            'domain': [('id','=',self.element_id.id)]
        }    
    
    def action_path(self):
        return {
            'name': 'Character Path',
            'type': 'ir.actions.act_window',
            'res_model': 'sr.path',
            'view_mode': 'form',
            'domain': [('id','=',self.path_id.id)]
        }


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
    img_id = fields.Many2one('ir.attachment', string='Image', domain="[('res_model','=','sr.element'),('res_field','=','img_id')]")
    
    @api.model_create_multi
    def create(self, vals_list):
        # On creation, look up image with corresponding name
        for vals in vals_list:
            if 'name' in vals:
                # Generate image attachment
                img_path = '/hsr_warp/static/icon/element/'
                vals['img_id'] = self.generate_image(img_path, vals['name']).id
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
    img_id = fields.Many2one('ir.attachment', string='Image', domain="[('res_model','=','sr.path'),('res_field','=','img_id')]")

    @api.model_create_multi
    def create(self, vals_list):
        # On creation, look up image with corresponding name
        for vals in vals_list:
            if 'name' in vals:
                # Generate image attachment
                img_path = '/hsr_warp/static/icon/path/'
                vals['img_id'] = self.generate_image(img_path, name=vals['name']).id
        return super(Path, self).create(vals_list)
    

class Warp(models.Model):
    # Override this model to add character link and compute
    _inherit = 'sr.warp'

    character_id = fields.Many2one('sr.character', compute='_compute_character_id')

    def _compute_character_id(self):
        for warp in self:
            warp.character_id = self.env['sr.character.template'].search([('character_id','=',warp.item_id)]) or None
