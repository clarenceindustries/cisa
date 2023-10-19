from odoo import models, fields, api,_

class StockQuant(models.Model):
    _inherit = "stock.quant"

    partner_id = fields.Many2one('res.partner', 'Fournisseur', readonly=True)
    producteur = fields.Char(string='Agricode', compute='_get_emb_info')
    subpackaging_id = fields.Many2one('stock.package.type',string='Sous-conditionnement', readonly=True, compute='_get_emb_info')
    subpackaging_count = fields.Integer(string='#', readonly=True, compute='_get_emb_info')
    weight = fields.Float(string='Poids net', compute='_weight', store=False)
    subpackaging_weight = fields.Float(string='Tare', compute='_subpackaging_weight', store=False)
    gross_weight = fields.Float(string='Poids brut', compute='_gross_weight', store=False)

    @api.depends('subpackaging_id', 'subpackaging_count')
    def _subpackaging_weight(self):
        for rec in self:
            subpackaging_weight = 0
            if rec.subpackaging_id:
                subpackaging_weight += rec.subpackaging_id.base_weight * rec.subpackaging_count
            rec.subpackaging_weight = subpackaging_weight

    api.depends('product_id', 'quantity')
    def _weight(self):
        for rec in self:
            rec.weight = rec.product_id._get_weight_from_qty(rec.quantity, from_uom_id=rec.product_uom_id)

    @api.depends('weight', 'subpackaging_weight')
    def _gross_weight(self):
        for rec in self:
            rec.gross_weight = rec.weight + rec.subpackaging_weight

    def _get_emb_info(self):
        for sq in self:
            in_res_sml = self.env['stock.move.line'].search([
                ('product_id', '=', sq.product_id.id),
                ('state', '=', 'done'),
                ('location_dest_id', '=', sq.location_id.id),
                ('lot_id', '=', sq.lot_id.id),
                ('result_package_id', '=', sq.package_id.id)])
            out_res_sml = self.env['stock.move.line'].search([
                ('product_id', '=', sq.product_id.id),
                ('state', '=', 'done'),
                ('location_id', '=', sq.location_id.id),
                ('lot_id', '=', sq.lot_id.id),
                ('package_id', '=', sq.package_id.id)])

            sq.producteur = ','.join(in_res_sml[0].mapped('lot_id.partner_ids.ref')) if in_res_sml else None
            sq.subpackaging_id = in_res_sml[0].subpackaging_id if in_res_sml else None
            sq.subpackaging_count = sum(in_res_sml.mapped('subpackaging_count')) - sum(out_res_sml.mapped('subpackaging_count'))