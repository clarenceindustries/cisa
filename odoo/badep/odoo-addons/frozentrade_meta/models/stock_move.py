from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')],
                                      'Type de transfert', required=True, related='picking_id.picking_type_code')
    subpackaging_count = fields.Integer(string='# carton/caisse', compute='_get_subpackaging_count')
    mrp_production_batch_id = fields.Many2one('mrp.production.batch', related='production_id.mrp_production_batch_id', store=True, readonly=True)
    # count_pallets = fields.Integer(string="Nbr palettes", tracking=True, compute='_get_count_pallets')
    # gross_weight = fields.Float(string="Poids brut", compute='_get_gross_weight')
    # dif_bl_done_qty = fields.Float(string='Écart', compute='_get_dif_bl_done_qty')
    # picking_type = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer')],
    #                         'Type de transfert', required=True, related='picking_id.picking_type_id.code')
    # gross_weight = fields.Float(digits='Account', string="Poids brut", compute='_get_gross_weight')
    # parent_categ = fields.Char(related='product_id.categ_id.parent_id.name', string='Catégorie parente')
    #
    # @api.depends('move_line_nosuggest_ids.gross_weight')
    # def _get_gross_weight(self):
    #     for sm in self:
    #         sm.gross_weight = sum(sml.gross_weight for sml in sm.move_line_nosuggest_ids)
    #
    # @api.depends('move_line_nosuggest_ids')
    # def _get_count_pallets(self):
    #     for sm in self:
    #         sm.count_pallets = 0
    #         v_count_pallets = 0
    #         for sml in sm.move_line_nosuggest_ids.mapped('result_package_id'):
    #             v_count_pallets += 1
    #         sm.count_pallets = v_count_pallets
    #
    #
    # @api.depends('move_line_nosuggest_ids.gross_weight')
    # def _get_gross_weight(self):
    #     for sm in self:
    #         sm.gross_weight = 0
    #         if sm.move_line_nosuggest_ids:
    #             sm.gross_weight = sum(sml.gross_weight for sml in sm.move_line_nosuggest_ids)
    #
    # @api.depends('product_uom_qty','quantity_done')
    # def _get_dif_bl_done_qty(self):
    #     for sm in self:
    #         sm.dif_bl_done_qty = 0
    #         if sm.product_uom_qty > 0 and sm.quantity_done > 0:
    #             sm.dif_bl_done_qty = sm.product_uom_qty-sm.quantity_done

    def _get_subpackaging_count(self):
        for sm in self:
            sm.subpackaging_count = 0
            for sml in sm.move_line_ids:
                sm.subpackaging_count += sml.subpackaging_count

    def action_show_details(self):
        if self.ids:
            res = super().action_show_details()
            res['context'].update({
                'show_package': not self.location_id.usage == 'supplier' and not self.location_id.usage == 'production'
            })
            return res
        return False