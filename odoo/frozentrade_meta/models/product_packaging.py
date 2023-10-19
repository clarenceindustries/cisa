# from odoo import models, fields, api
#
# class StockPackageType(models.Model):
#     _inherit = "stock.package.type"
    # _rec_name = 'name'

    # max_weight = fields.Float("Maximum Weight", compute='_get_max_weight')
    # # related_article = fields.Many2one('product.product', string='Article lié')
    # #
    # # def name_get(self):
    # #     return [(pp.id, pp.name) for pp in self]
    #
    # @api.depends('base_weight','qty')
    # def _get_max_weight(self):
    #     for pp in self:
    #         if pp.product_id:
    #             pp.max_weight = pp.base_weight + pp.product_id._get_weight_from_qty(pp.qty, from_uom_id=pp.product_uom_id, to_uom_id=pp.weight_uom_id)
    #         else:
    #             pp.max_weight = pp.base_weight