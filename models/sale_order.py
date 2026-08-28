# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # La orden creada desde "Sales Orders" NACE como orden de venta. La marca
    # persiste porque el formulario puede guardarse ANTES de tener líneas
    # (al abrir un asistente: comprobante de pago, eliminar IVA, WhatsApp,
    # selector de placas…); en ese momento no se puede confirmar, y sin la
    # marca la orden se quedaba como cotización para siempre.
    x_born_confirmed = fields.Boolean(
        string='Nació como orden de venta', copy=False, index=True,
        help='Creada desde Sales Orders: se confirma sola en cuanto tenga líneas.')

    @api.model_create_multi
    def create(self, vals_list):
        """Desde el menú "Sales Orders" (contexto 'create_confirmed_order')
        la orden nace confirmada: se ejecuta la confirmación completa
        (action_confirm) sin pasar por cotización."""
        born = bool(self.env.context.get('create_confirmed_order'))
        if born:
            for vals in vals_list:
                vals.setdefault('x_born_confirmed', True)
        orders = super().create(vals_list)
        if born:
            orders._born_confirm_if_ready()
        return orders

    def write(self, vals):
        res = super().write(vals)
        # Se agregaron líneas a una orden que nació como venta y sigue en
        # borrador: confirmar ahora.
        if 'order_line' in vals and not self.env.context.get('born_confirm_running'):
            self.filtered(lambda o: o.x_born_confirmed and o.state == 'draft')._born_confirm_if_ready()
        return res

    def _born_confirm_if_ready(self):
        for order in self:
            # Solo borradores con líneas reales; nunca los respaldos de
            # cotización que genera sale_stone_selection al confirmar.
            if order.state != 'draft' or not order.x_born_confirmed:
                continue
            if getattr(order, 'x_is_quote_backup', False):
                continue
            if not order.order_line.filtered(lambda l: not l.display_type):
                continue
            # create_confirmed_order=False: dentro de action_confirm,
            # sale_stone_selection hace order.copy() para el respaldo de
            # cotización y ese copy HEREDA el contexto — volvía a entrar
            # aquí y a confirmar el respaldo (folio V/ quemado y COT/
            # fantasma).
            order.with_context(
                skip_sale_order_redirect=True,
                create_confirmed_order=False,
                born_confirm_running=True,
            ).action_confirm()

    def action_confirm(self):
        """Redirige al formulario dentro de Sales Orders tras confirmar una
        cotización desde la UI; durante la creación (orden que nace
        confirmada) el resultado se ignora."""
        res = super().action_confirm()
        if self.env.context.get('skip_sale_order_redirect'):
            return res
        if self and len(self) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.id,
                'view_mode': 'form',
                'views': [(False, 'form')],
                'target': 'current',
                'context': dict(self.env.context),
            }
        return res
