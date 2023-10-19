from odoo import models, fields, api, exceptions, _


class GscDriver(models.Model):
    _name = "gsc.driver"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Conducteur'

    partner_id = fields.Many2one("res.partner", string="Related Partner", required=True, ondelete="restrict", delegate=True, auto_join=True)
    cin  = fields.Char(string='CIN', required=True)
    is_driver = fields.Boolean(string="Conducteur ?", default=True)

class GscFleet(models.Model):
    _name = "gsc.fleet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Camion'

    name = fields.Char(string="Matricule", required=True)
    model_marque_id = fields.Char(string="Modéle/Marque", required=True)
    driver_id = fields.Many2one('gsc.driver', string='Conducteur', required=True)
    cin = fields.Char(string='CIN Conducteur', related='driver_id.cin')
    partner_id = fields.Many2one('res.partner', string='Société')