from odoo import models, fields, api, _, exceptions
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_view_purchase_order(self):
        purchase = self.purchase_id
        if not purchase:
            return self.create_po_btn()
        

        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        action['res_id'] = purchase and purchase.id 

        return action

    def create_po_btn(self):
        self.ensure_one()
        if self.purchase_id:
            return self.action_view_purchase_order()
        po_obj = self.env['purchase.order']
        
        fiscal_position_id = self.env['account.fiscal.position'].sudo().with_context(company_id=self.company_id)._get_fiscal_position(self.partner_id)
        purchase_order = po_obj.create( {
            'partner_id': self.partner_id.id,
            'currency_id': self.partner_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
            'payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'fiscal_position_id': fiscal_position_id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'date_order': self.scheduled_date,
            
        })

        for line in self.move_ids:
            
            # purchase_qty_uom = line.product_uom._compute_quantity(line.quantity, line.product_id.uom_po_id)

            supplierinfo = line.product_id._select_seller(
                partner_id = purchase_order.partner_id,
                quantity = line.product_uom_qty,
                date = purchase_order.date_order and purchase_order.date_order.date(), 
                uom_id = line.product_id.uom_po_id
            )
            fpos = purchase_order.fiscal_position_id
            taxes = fpos.map_tax(line.product_id.supplier_taxes_id) if fpos else line.product_id.supplier_taxes_id
            if taxes:
                taxes = taxes.filtered(lambda t: t.company_id.id == self.company_id.id)

            # compute unit price
            price_unit = 0.0
            if supplierinfo:
                price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, line.product_id.supplier_taxes_id, taxes, self.company_id)
                if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                    price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

            # purchase line description in supplier lang
            product_in_supplier_lang = line.product_id.with_context({
                'lang': supplierinfo.partner_id.lang,
                'partner_id': supplierinfo.partner_id.id,
            })
            name = '[%s] %s' % (line.product_id.default_code, product_in_supplier_lang.display_name)
            if product_in_supplier_lang.description_purchase:
                name += '\n' + product_in_supplier_lang.description_purchase

            po_order_line = self.env['purchase.order.line'].create( {
                'name': line.name,
                'product_qty': line.product_uom_qty,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'price_unit': price_unit,
                'order_id' : purchase_order.id,
                'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(supplierinfo.delay)),
                'taxes_id': [(6, 0, taxes.ids)],
            })
            line.purchase_line_id = po_order_line
        # self.purchase_id = purchase_order.id
        # purchase_order.invoice_ids = self
        result = self.env.ref('purchase.purchase_rfq').read()[0]
        res = self.env.ref('purchase.purchase_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = purchase_order.id or False

        return result

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for line in self.mapped('order_line.move_ids'):
            line.price_unit = line._get_price_unit()
            line.stock_valuation_layer_ids.sudo().unlink()
            self.env['stock.move.line']._create_correction_svl(line, line.product_qty)

        for po in self:
            for sp in po.picking_ids:
                sp.origin = po.name
        return super().button_confirm()