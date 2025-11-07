# -*- coding: utf-8 -*-
import base64
import os
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _huby_static_image_base64(self, filename):
        """Return the base64 representation of a static image bundled in the module."""
        if not filename:
            return False
        resource_path = get_module_resource('huby_personalize', 'static', 'src', 'img', filename)
        if not resource_path:
            return False
        try:
            with open(resource_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('ascii')
        except OSError:
            return False

    def _huby_sale_logo(self):
        """Retorna el logo de HUBY en base64 para el reporte de cotización."""
        return self._huby_static_image_base64('logo.png')

    def _huby_sale_tagline(self):
        """Retorna el banner/lema de HUBY en base64 para el reporte de cotización."""
        return self._huby_static_image_base64('lema.png')

    def _huby_sale_footer(self):
        """Retorna el pie de página de HUBY en base64 para el reporte de cotización."""
        return self._huby_static_image_base64('pie_pagina.png')

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

    @api.constrains('attended_by_employee_id')
    def _check_attended_by_employee(self):
        """
        Validar que el campo 'Atendido por' esté lleno antes de guardar
        """
        for order in self:
            if not order.attended_by_employee_id:
                raise ValidationError(
                    'Debe seleccionar el empleado que atiende esta orden de venta.'
                )
