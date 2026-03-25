# -*- coding: utf-8 -*-
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """
        Override para redirigir al usuario a la vista de Sales Orders
        después de confirmar una cotización.
        """
        res = super().action_confirm()

        # Si la confirmación fue exitosa y estamos en la UI (no en batch/cron),
        # redirigimos al formulario de la orden dentro del menú Sales Orders
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
