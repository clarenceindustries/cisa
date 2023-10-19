from odoo import models, fields, api

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    picking_type = fields.Selection([
        ('mo_psf', 'MO PSF'),
        ('mo_pf', 'MO PF')], string="Type de production")
    remove_scraps_from_qty_received = fields.Boolean('Enlever les rebuts des quantités reçues', default=True)
    allow_multiple_products = fields.Boolean('Autoriser plusieurs produits dans le transfert', default=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unités opérationnelles')