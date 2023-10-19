from odoo import models, fields, api, exceptions, _

class gscFarm(models.Model):
    _name = "gsc.farm"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ferme'

    name = fields.Char(string="Ferme", required=True)
    owner_id = fields.Many2one('res.partner', string="Producteur", required=True)
    adress = fields.Char('Région', required=True)
    distance_factory_farm = fields.Float(string='Dist Ferme/Usine (KM)')
    area = fields.Float(string="Surface (HÉC)")