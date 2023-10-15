from odoo import api, fields, models, tools

class Warp(models.Model):
    _name = "sr.warp"
    _description = "Warp"

    uid = fields.Char(string="User ID")
    gacha_id = fields.Char(string="Banner ID")
    gacha_type = fields.Char(string="Banner Type")
    item_id = fields.Char(string="Item ID")
    count = fields.Char(string="Count")
    time = fields.Char(string="Time")
    name = fields.Char(string="Name")
    lang = fields.Char(string="Lang")
    item_type = fields.Char(string="Item Type")
    rank_type = fields.Char(string="Rarity")
    wid = fields.Char(string="Warp ID")