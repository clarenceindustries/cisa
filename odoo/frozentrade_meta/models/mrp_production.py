from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    prct_production = fields.Float(string='Rendement', compute='_get_prct_production', digits=(16, 3))
    qty_producing = fields.Float(string="Quantity Producing", digits='Product Unit of Measure', copy=False, compute='_qty_producing', store=True, readonly=True)
    move_product_finished_ids = fields.One2many('stock.move', compute='_compute_move_product_finished_ids')

    @api.depends('move_finished_ids')
    def _compute_move_product_finished_ids(self):
        for order in self:
            order.move_product_finished_ids = order.move_finished_ids.filtered(lambda m: m.product_id == order.product_id)

    def action_confirm(self):
        for rec in self:
            rec.action_generate_serial()
        return super().action_confirm()

    @api.depends('move_finished_ids.quantity_done')
    def _qty_producing(self):
        for rec in self:
            rec.qty_producing = sum(rec.move_finished_ids.filtered(lambda x: x.product_id == rec.product_id).mapped('quantity_done'))
            # rec._set_qty_producing()

    def _post_inventory(self, cancel_backorder=False):
        for rec in self.filtered(lambda x: x.lot_producing_id):
            rec.finished_move_line_ids.filtered(lambda x: x.product_id == rec.product_id).lot_id = rec.lot_producing_id
        res = super()._post_inventory(cancel_backorder)
        return res

    def get_suitable_batches(self, vals):
        batches = self.env['mrp.production.batch'].search([
            ('state', '=', 'draft'),
            ('picking_type_id', '=', vals.get('picking_type_id')),
            ('routing_id', '=', vals.get('routing_id'))
        ])
        attribute_values = self.env['product.product'].browse(vals['product_id']).product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.group_in_mrp_batch)
        result = batches.filtered(lambda b: (attribute_values in b.attribute_value_ids or attribute_values == b.attribute_value_ids) and b.product_category_id.id == self.env['product.product'].browse(vals['product_id']).categ_id.id)
        return result

    def button_mark_done(self):
        for rec in self.filtered(lambda x: x.lot_producing_id):
            rec.lot_producing_id.partner_ids = rec.move_raw_ids.filtered(lambda x: x.product_id.categ_id.family in ('matiere_premiere', 'produit_semi_fini')
                                                                         or x.product_id.categ_id.parent_id.family in ('matiere_premiere', 'produit_semi_fini')).mapped('move_line_ids.lot_id.partner_ids')
        return super().button_mark_done()

    @api.depends('move_raw_ids.quantity_done', 'move_byproduct_ids.quantity_done')
    def _get_prct_production(self):
        for mp in self:
            mp.prct_production = 0
            qty_raw_materiel = 0
            qty_byproduct = 0
            if mp.product_id.categ_id.family in ('produit_semi_fini', 'produit_fini') \
                    or mp.product_id.categ_id.parent_id.family in ('produit_semi_fini', 'produit_fini'):
                for mr in mp.move_raw_ids:
                    if mr.product_id.categ_id.family in ('matiere_premiere', 'produit_semi_fini') \
                            or mr.product_id.categ_id.parent_id.family in ('matiere_premiere', 'produit_semi_fini'):
                        qty_raw_materiel += mr.quantity_done
                for mb in mp.move_byproduct_ids:
                    qty_byproduct += mb.quantity_done
            if qty_raw_materiel != 0:
                mp.prct_production = 100 * mp.qty_producing/qty_raw_materiel