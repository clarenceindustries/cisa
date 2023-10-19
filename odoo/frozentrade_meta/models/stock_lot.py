from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    scrap_ids = fields.One2many('stock.scrap', 'lot_id')
    partner_ids = fields.Many2many('res.partner', string='Producteur')
    packing_date = fields.Date(string='Packing Date', compute='_get_packing_date')

    def _get_packing_date(self):
        for spq in self:
            spq.packing_date = False
            obj_mrp = self.env['mrp.production'].search([('lot_producing_id','=',spq.id)], limit=1)
            if obj_mrp:
                spq.packing_date = obj_mrp.date_finished