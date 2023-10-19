from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # Champs expédition
    packing_date = fields.Date(string='Packing Date', compute='_get_packing_date')
    subpackaging_id = fields.Many2one('stock.package.type', string='Sous-conditionnement',
                                      domain="[('type','=','caisse')]",
                                      tracking=True)
    subpackaging_count = fields.Integer(string='#')
    weight_packaging = fields.Float(digits='Account', string='Tare', compute='_get_weight_packaging', store=True)
    weight_subpackaging = fields.Float(digits='Account', string='Tare Sous-conditionnement', compute='_get_weight_subpackaging', store=True)
    initial_gross_weight = fields.Float(digits='Account', string="Poids brut initial")
    gross_weight = fields.Float(digits='Account', string="Poids brut")
    weight_uom_id = fields.Many2one('uom.uom', related='product_id.weight_uom_id')

    @api.constrains('package_id', 'result_package_id')
    def _fill_package_info(self):
        for sml in self:
            if sml.package_id and sml.package_id == sml.result_package_id:
                sml.subpackaging_id = sml.package_id.quant_ids[0].subpackaging_id
                sml.subpackaging_count = sml.package_id.quant_ids[0].subpackaging_count
                sml.initial_gross_weight = sml.result_package_id.weight

    @api.depends('result_package_id', 'subpackaging_id', 'subpackaging_count')
    def _get_weight_packaging(self):
        for rec in self:
            weight_packaging = 0
            # if not rec._origin:
            #     all_moves = self.env.cache.get_records(rec.move_id.move_line_ids, rec._fields['move_id']) - rec
            # else:
            #     all_moves = self.env.cache.get_records(rec.move_id.move_line_ids, rec._fields['move_id'])
            if rec.result_package_id and rec.result_package_id.package_type_id:
                weight_packaging += rec.result_package_id.package_type_id.base_weight
            if rec.subpackaging_id and rec.subpackaging_count > 0:
                weight_packaging += rec.subpackaging_id.base_weight * rec.subpackaging_count
            rec.weight_packaging = weight_packaging

    @api.depends('subpackaging_id', 'subpackaging_count')
    def _get_weight_subpackaging(self):
        for rec in self:
            weight_packaging = 0
            if rec.subpackaging_id and rec.subpackaging_count > 0:
                weight_packaging += rec.subpackaging_id.base_weight * rec.subpackaging_count
            rec.weight_subpackaging = weight_packaging

    @api.onchange('weight_packaging', 'gross_weight', 'product_uom_id', 'weight_uom_id')
    def _get_quantity_done(self):
        for sml in self:
            if sml.gross_weight > sml.weight_packaging:
                weight_done = sml.gross_weight - sml.weight_packaging
                sml.qty_done = sml.product_id._get_qty_from_weight(weight_done, from_uom_id=sml.weight_uom_id,
                                                                   to_uom_id=sml.product_uom_id)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if res.get('product_id', False) and res.get('picking_id', False):
            product = self.env['product.product'].browse(res['product_id'])
            picking = self.env['stock.picking'].browse(res['picking_id'])
            partner = picking.partner_id
            if product.default_code and picking.carrier_tracking_ref and partner.ref:
                res.update({
                    'lot_name': '%s.%s.%s' % (partner.ref, picking.carrier_tracking_ref, product.default_code)
                })
        return res

    @api.model
    def create(self, vals):
        if not vals.get('lot_id', False) and not vals.get('lot_name', False):
            if vals.get('product_id', False) and vals.get('picking_id', False):
                product = self.env['product.product'].browse(vals['product_id'])
                picking = self.env['stock.picking'].browse(vals['picking_id'])
                partner = picking.partner_id
                if product.default_code and picking.carrier_tracking_ref and partner.ref:
                    vals.update({
                        'lot_name': '%s.%s.%s' % (partner.ref, picking.carrier_tracking_ref, product.default_code)
                    })
        return super().create(vals)

    @api.depends('lot_id')
    def _get_packing_date(self):
        for sml in self:
            sml.packing_date = False
            if sml.lot_id:
                obj_mrp = sml.env['mrp.production'].search([('lot_producing_id', '=', sml.lot_id.id)], limit=1)
                if obj_mrp:
                    self.packing_date = obj_mrp.date_finished

    def _get_agricode(self):
        for sml in self:
            agricode = None
            if sml.lot_id:
                obj_mrp = sml.env['mrp.production'].search([('lot_producing_id', '=', sml.lot_id.id)])
                agricode = ', '.join(obj_mrp.mapped('move_raw_ids.lot_ids.purchase_order_ids.partner_id.ref'))
            if not agricode:
                for sm in sml.move_id.production_id.move_raw_ids:
                    for sml2 in sm.move_line_ids:
                        if sml2.package_id.producteur: 
                            agricode = sml2.package_id.producteur
        return agricode

    @api.onchange('qty_done')
    def _onchange_qty_done(self):
        for sml in self:
            if sml.qty_done != 0:
                if not sml.result_package_id and sml.product_id.categ_id.restrict_to_packaging and sml.location_dest_usage == 'internal':
                    raise exceptions.ValidationError("Veuillez remplir la palette de destination !!!")
