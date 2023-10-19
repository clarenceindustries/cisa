from odoo import models, fields, api

class QuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    date_reception = fields.Datetime(string='Date réception', compute='_set_reception_info')
    producteur = fields.Char(string='Agricode', compute='_set_reception_info')

    partner_ids = fields.Many2many('res.partner', string='Fournisseurs', compute='_partner_ids')
    subpackaging_ids = fields.Many2many('stock.package.type', string='Sous-emballage', compute='_subpackaging_ids')
    subpackaging_count = fields.Integer(string='# de sous emballage', compute='_subpackaging_count', store=False)
    packaging_weight = fields.Float(string='Tare', compute='_packaging_weight', store=False)
    net_weight = fields.Float(string='Poids net', digits='Stock Weight', compute='_net_weight', store=False)

    @api.depends('quant_ids')
    def name_get(self):
        res = super().name_get()
        name_mapping = dict(res)
        for rec in self.filtered(lambda x: x.net_weight):
            name_mapping[rec.id] = '%s - %skg (%s)' % (name_mapping[rec.id], rec.net_weight, ','.join(rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal').mapped('product_id.display_name')))
        return list(name_mapping.items())

    @api.depends('quant_ids.weight')
    def _net_weight(self):
        for rec in self:
            rec.net_weight = sum(rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal').mapped('weight'))

    @api.depends('net_weight', 'weight')
    def _packaging_weight(self):
        for rec in self:
            rec.packaging_weight = rec.weight - rec.net_weight

    @api.depends('quant_ids.partner_id')
    def _partner_ids(self):
        for rec in self:
            rec.partner_ids = rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal').mapped('partner_id')

    @api.depends('quant_ids.subpackaging_id')
    def _subpackaging_ids(self):
        for rec in self:
            rec.subpackaging_ids = rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal').mapped('subpackaging_id')

    @api.depends('quant_ids', 'quant_ids.subpackaging_count')
    def _subpackaging_count(self):
        for rec in self:
            rec.subpackaging_count = sum(rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal').mapped('subpackaging_count'))

    @api.depends('quant_ids', 'package_type_id')
    def _compute_weight(self):
        super()._compute_weight()
        for rec in self:
            rec.weight += sum(rec.quant_ids.filtered(lambda x: x.location_id.usage == 'internal' and x.subpackaging_id).mapped('subpackaging_weight'))

    @api.depends('quant_ids')
    def _set_reception_info(self):
        for sqp in self:
            sqp.producteur = None
            sqp.date_reception = None
            for sq in sqp.quant_ids:
                in_res_sml = self.env['stock.move.line'].search([
                    ('product_id', '=', sq.product_id.id),
                    ('state', '=', 'done'),
                    ('location_dest_id', '=', sq.location_id.id),
                    ('result_package_id', '=', sq.package_id.id),
                    ('lot_id','=', sq.lot_id.id)], order='id desc')
                out_res_sml = self.env['stock.move.line'].search([
                    ('product_id', '=', sq.product_id.id),
                    ('state', '=', 'done'),
                    ('location_id', '=', sq.location_id.id),
                    ('package_id', '=', sq.package_id.id),
                    ('lot_id', '=', sq.lot_id.id),])
                if in_res_sml:
                    sqp.producteur = ','.join(in_res_sml[0].mapped('lot_id.partner_ids.ref'))
                    sqp.pack_date = in_res_sml[0].picking_id.date_done if in_res_sml[0].picking_id.date_done else in_res_sml[0].packing_date
                    sqp.date_reception = in_res_sml[0].picking_id.date_done