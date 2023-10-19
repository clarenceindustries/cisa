from odoo import models, fields, api

class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    type = fields.Selection([('container', 'Conteneur'), ('pallet', 'Palette'), ('caisse', 'Caisse')], required=True, default='pallet')