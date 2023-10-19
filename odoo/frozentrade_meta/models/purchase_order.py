from odoo import models, fields, api,_
from odoo.exceptions import UserError

# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"
#     @api.onchange("operating_unit_id")
#     def _onchange_operating_unit_id(self):
#         type_obj = self.env["stock.picking.type"]
#         if self.operating_unit_id:
#             types = type_obj.search(
#                 [
#                     ("code", "=", "incoming"),
#                     ("default_location_dest_id.operating_unit_id", "=", self.operating_unit_id.id),
#                 ], limit=1
#             )
#             if types:
#                 self.picking_type_id = types
#             else:
#                 raise UserError(
#                     _(
#                         "No Warehouse found with the Operating Unit indicated "
#                         "in the Purchase Order"
#                     )
#                 )
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.order_id.state in ['purchase', 'done']:
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                elif line.product_id.purchase_method == 'min_cmd_recep':
                    line.qty_to_invoice = min((line.qty_received - line.qty_invoiced), (line.product_qty - line.qty_invoiced))
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('move_ids.state', 'move_ids.product_uom_qty', 'move_ids.product_uom', 'move_ids.move_line_ids.lot_id.scrap_ids.state')
    def _compute_qty_received(self):
        super(PurchaseOrderLine, self)._compute_qty_received()
        for line in self:
            scraps = line.mapped('move_ids.move_line_ids.lot_id.scrap_ids').filtered(lambda s: s.state == 'done' and s.picking_id.picking_type_id.remove_scraps_from_qty_received)
            if scraps:
                #TODO: take in consideration uom conversion
                line.qty_received = line.qty_received - sum(scraps.mapped('scrap_qty'))

