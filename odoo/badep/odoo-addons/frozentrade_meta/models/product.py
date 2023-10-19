from odoo import models, fields, api, exceptions


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight = fields.Float('Weight', digits='Stock Weight', compute='_get_weight_from_uom')

    @api.depends('uom_id', 'weight_uom_id')
    def _get_weight_from_uom(self):
        for rec in self:
            rec.weight  = 0
            if rec.uom_id.category_id == self.env.ref('uom.product_uom_categ_kgm'):
                rec.weight = rec.uom_id._compute_quantity(1, rec.weight_uom_id)

    def _get_weight_from_qty(self, qty, from_uom_id=False, to_uom_id=False):
        self.ensure_one()
        from_uom_id = from_uom_id or self.uom_id
        to_uom_id = to_uom_id or self.weight_uom_id
        return self.weight_uom_id._compute_quantity(from_uom_id._compute_quantity(qty, self.uom_id) * self.weight, to_uom_id)

    def _get_qty_from_weight(self, weight, from_uom_id=False, to_uom_id=False):
        self.ensure_one()
        res = None
        from_uom_id = from_uom_id and from_uom_id or self.uom_id
        to_uom_id = to_uom_id and to_uom_id or self.weight_uom_id
        if self.weight > 0:
            res = self.uom_id._compute_quantity(from_uom_id._compute_quantity(weight, self.weight_uom_id) / self.weight, to_uom_id)
        else:
            raise exceptions.ValidationError("Veuillez remplir le poids dans le produit {}".format(self.name))


        return res

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_method = fields.Selection(selection_add=[('min_cmd_recep', 'Min (commandé, réceptionné)')])
    weight_uom_id = fields.Many2one('uom.uom', compute='_weight_uom_id')

    def _weight_uom_id(self):
        for rec in self:
            rec.weight_uom_id = rec._get_weight_uom_id_from_ir_config_parameter()