# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_name = fields.Char(
        string='Nombre del Proyecto',
        help='Nombre del proyecto asociado a esta cotización',
        required=True,
        tracking=True,
    )

    # Campo para empleado que atiende
    attended_by_employee_id = fields.Many2one(
        'hr.employee',
        string='Atendido por',
        help='Empleado que atiende esta cotización',
        tracking=True,
    )

    # Campos para fechas de entrega
    delivery_date_first = fields.Datetime(
        string='Fecha de Entrega',
        help='Fecha y hora de entrega inicial. Una vez establecida, no se puede modificar.',
        default=fields.Datetime.now,
        tracking=True,
        copy=False,
    )

    delivery_date_second = fields.Datetime(
        string='Segunda Fecha de Entrega',
        help='Fecha de entrega ajustada. Requiere empleado responsable y justificación.',
        tracking=True,
        copy=False,
    )

    delivery_change_employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado Responsable del Cambio',
        help='Empleado que autoriza o realiza el cambio de fecha de entrega',
        tracking=True,
        copy=False,
    )

    delivery_change_justification = fields.Text(
        string='Justificación del Cambio',
        help='Motivo del cambio en la fecha de entrega',
        tracking=True,
        copy=False,
    )

    # Campo computado para saber si la primera fecha ya fue establecida
    is_delivery_date_locked = fields.Boolean(
        string='Primera Fecha Bloqueada',
        compute='_compute_is_delivery_date_locked',
        store=False,
    )

    @api.depends('delivery_date_first')
    def _compute_is_delivery_date_locked(self):
        """
        Una vez que se crea el registro con la fecha inicial,
        se bloquea la edición de la primera fecha
        """
        for order in self:
            # Si el registro ya existe (tiene ID) y tiene fecha inicial, está bloqueado
            order.is_delivery_date_locked = bool(order.id and order.delivery_date_first)

    @api.constrains('delivery_date_second', 'delivery_change_employee_id', 'delivery_change_justification')
    def _check_second_delivery_date_requirements(self):
        """
        Validar que si se establece una segunda fecha de entrega,
        también se proporcione empleado y justificación
        """
        for order in self:
            if order.delivery_date_second:
                if not order.delivery_change_employee_id:
                    raise ValidationError(
                        'Debe seleccionar un empleado responsable del cambio de fecha de entrega.'
                    )
                if not order.delivery_change_justification:
                    raise ValidationError(
                        'Debe proporcionar una justificación para el cambio de fecha de entrega.'
                    )
