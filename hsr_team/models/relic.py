from odoo import api, fields, models, Command

    
class RelicSet(models.Model):
    _name = 'sr.relic.set'
    _description = 'Relic Set'
    _inherit = 'sr.image.mixin'

    set_id = fields.Integer('Set ID')
    name = fields.Char('Set')

    is_ornament = fields.Boolean('Ornament Set')
    is_relic = fields.Boolean('Relic Set')
    bonus_two = fields.Char('2-Set Bonus')
    bonus_four = fields.Char('4-Set Bonus')
    
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    @api.depends('set_id')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        # Icon format will be 'icon/relic/116.png'
        img_path = '/hsr_warp/static/icon/relic/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path + rec.set_id).id


class Relic(models.Model):
    _name = 'sr.relic'
    _description = 'Relic'
    _inherit = 'sr.item'

    set_id = fields.Many2one('sr.relic.set')
    main_affix_id = fields.Many2one('sr.attribute')
    sub_affix_ids = fields.One2many('sr.attribute', 'relic_id')
    character_id = fields.Many2one('sr.character', string='Equipped By')

    icon = fields.Char('Icon Image Path')
    img_id = fields.Many2one('ir.attachment', string='Image', compute='_compute_img_id')

    # score = fields.Float('Relic Score')

    def name_get(self):
        return [(rec.id, f"{rec.set_id.name}: {rec.relic_name}") for rec in self]
    
    @api.depends('icon')
    def _compute_img_id(self):
        # Get image attachment when updating item_id
        # Icon format will be 'icon/relic/116_2.png'
        img_path = '/hsr_warp/static/'
        for rec in self:
            rec.img_id = rec.get_image_from_path(img_path + rec.icon).id

    @api.model_create_multi
    def create(self, vals_list):
        relics = super().create(vals_list)
        for relic in relics:
            relic.main_affix_id.relic_main_id = relic.id

    def _populate_relics(self, data):
        '''
            id          - Object ID, str
            name        - Name of relic, str
            set_id      - Relic set ID, str
            set_name    - Relic set name, str
            rarity      - Star Rarity, int
            level       - Relic Level, int
            icon        - Relic Image Path, str
            main_affix  - Primary Relic Stat, dict
            sub_affix   - Relic Substats, list(dict)
        '''
        to_remove = ['set_name']
        commands = [Command.clear()]
        Attribute = self.env['sr.attribute']
        for rel in data:
            # Remove key if exists
            for k in to_remove: rel.pop(k, None) 
            # Rename id key to db friendly, cast to int for lookup
            rel['item_id'] = int(rel.pop('id'))
            # Typecast fields for easy storing
            rel['rarity'] = str(rel.pop('rarity'))
            # Locate set id by reference
            rel['set_id'] = self.env.ref('hsr_team.relic_set_' + rel.pop('set_id')).id
            # Convert affixes into sr.attribute
            rel['main_affix_id'] = Attribute._create_main_affix(rel.pop('main_affix'))
            rel['sub_affix_ids'] = Attribute._populate_attributes(rel.pop('sub_affix'))
            commands.append(Command.create(rel))
        return commands
    
