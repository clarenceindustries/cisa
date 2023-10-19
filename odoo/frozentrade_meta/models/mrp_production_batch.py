from odoo import models, fields, api, _


class MrpProductionBatch(models.Model):
    _inherit = "mrp.production.batch"

    product_category_id = fields.Many2one('product.category', string="Catégorie d'article", compute='_get_product_category')
    disponible_pm = fields.Float(string="Disponible", compute='_get_disponible')
    qty_production = fields.Float(string="Qté production", compute='_get_qty_production')
    dechets = fields.Float(string="Qté déchets", compute='_get_dechets')
    perte = fields.Float(string="Perte", compute='_get_perte')
    prct_rendement = fields.Float(string="Rendement", compute='_get_prct_rendement')

    @api.depends('move_batch_ids')
    def _get_disponible(self):
        for mpb in self:
            if mpb.state != 'cancel':
                mpb.disponible_pm = sum(mpb.move_batch_ids.filtered(lambda x: x.product_id.categ_id.family in ('matiere_premiere', 'produit_semi_fini')
                                                                        or x.product_id.categ_id.parent_id.family in ('matiere_premiere', 'produit_semi_fini')).mapped('reserved_availability'))
            else:
                mpb.disponible_pm = 0
                

    @api.depends('move_batch_ids')
    def _get_qty_production(self):
        for mpb in self:
            if mpb.state == 'done':
                mpb.qty_production = sum(mpb.move_batch_ids.filtered(lambda x: x.product_id.categ_id.family in ('matiere_premiere', 'produit_semi_fini')
                                                                        or x.product_id.categ_id.parent_id.family in ('matiere_premiere', 'produit_semi_fini')).mapped('quantity_done'))
            else:
                mpb.qty_production = 0

    @api.depends('move_byproduct_ids')
    def _get_dechets(self):
        for mpb in self:
            if mpb.state == 'done':
                mpb.dechets = sum(l.quantity_done for l in mpb.move_byproduct_ids)
            else:
                mpb.dechets = 0


    @api.depends('disponible_pm','qty_production','dechets')
    def _get_perte(self):
        for mpb in self:
            if mpb.state == 'done':
                mpb.perte = mpb.disponible_pm- mpb.qty_production - mpb.dechets
            else:
                mpb.perte = 0

    @api.depends('production_ids')
    def _get_prct_rendement(self):
        for mpb in self:
            mpb.prct_rendement = sum(mp.prct_production * mp.qty_producing for mp in mpb.production_ids.filtered(lambda x: x.state != 'cancel'))/sum(mpb.production_ids.filtered(lambda x: x.state != 'cancel').mapped('qty_producing')) if sum(mpb.production_ids.filtered(lambda x: x.state != 'cancel').mapped('qty_producing')) > 0 else 0

    @api.depends('production_ids')
    def _get_product_category(self):
        for mpb in self:
            mpb.product_category_id = None
            if mpb.production_ids:
                mpb.product_category_id = mpb.production_ids[0].product_id.categ_id.id


    def action_confirm(self):
        for mpb in self:
            mpb.action_update_move_data()
        return super().action_confirm()
