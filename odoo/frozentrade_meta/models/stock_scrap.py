from odoo import fields, models, api, exceptions, _

class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.onchange('picking_id')
    def _domain_lot_id(self):
        for ss in self:
            if ss.picking_id:
                return {'domain': {'lot_id': [('id','in',ss.picking_id.move_line_ids_without_package.mapped('lot_id.id'))]}}

    @api.onchange('picking_id','lot_id')
    def _domain_package_id(self):
        for ss in self:
            if ss.picking_id and not ss.lot_id:
                return {'domain': {'package_id': [('id','in',ss.picking_id.move_line_ids_without_package.mapped('package_id.id'))]}}
            elif ss.picking_id and ss.lot_id:
                return {'domain': {'package_id': [('id','in',ss.picking_id.move_line_ids_without_package.filtered(lambda sml: sml.lot_id.id == ss.lot_id.id).mapped('package_id.id'))]}}

    def action_validate(self):
        res = super().action_validate()
        for ss in self:
            
            if not ss.production_id:

                if ss.lot_id and not ss.package_id:
                    list_product_uom_qty = ss.picking_id.move_line_ids.filtered(lambda sml: sml.lot_id.id == ss.lot_id.id).mapped('qty_done')
                    total_picking_qty = sum(val for val in list_product_uom_qty)
                    if ss.scrap_qty > total_picking_qty:
                        raise exceptions.ValidationError(_('la quantité scrapée est supérieure à la quantité dans le lot {}'.format(ss.lot_id.name)))

                elif ss.lot_id and ss.package_id:
                    list_product_uom_qty = ss.picking_id.move_line_ids.filtered(lambda sml: sml.result_package_id.id == ss.package_id.id).mapped('qty_done')
                    total_picking_qty = sum(val for val in list_product_uom_qty)
                    if ss.scrap_qty > total_picking_qty:
                        raise exceptions.ValidationError(_('la quantité scrapée est supérieure à la quantité dans {}'.format(ss.package_id.name)))

            if ss.production_id:
                
                if ss.lot_id and not ss.package_id:
                    list_product_uom_qty = ss.production_id.finished_move_line_ids.filtered(lambda sml: sml.lot_id.id == ss.lot_id.id).mapped('qty_done')
                    total_picking_qty = sum(val for val in list_product_uom_qty)
                    print('.....................total_picking_qty1', total_picking_qty)
                    if ss.scrap_qty > total_picking_qty:
                        raise exceptions.ValidationError(_('la quantité scrapée est supérieure à la quantité dans le lot {}'.format(ss.lot_id.name)))

                elif ss.lot_id and ss.package_id:
                    list_product_uom_qty = ss.production_id.finished_move_line_ids.filtered(lambda sml: sml.result_package_id.id == ss.package_id.id).mapped('qty_done')
                    total_picking_qty = sum(val for val in list_product_uom_qty)
                    print('.....................total_picking_qty2', total_picking_qty)
                    if ss.scrap_qty > total_picking_qty:
                        raise exceptions.ValidationError(_('la quantité scrapée est supérieure à la quantité dans {}'.format(ss.package_id.name)))
        return res