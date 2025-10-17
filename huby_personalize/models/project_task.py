# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        'task_id',
        string='Líneas de Orden de Venta',
        help='Líneas de productos asociadas a esta tarea'
    )

    products_count = fields.Integer(
        string='Cantidad de Productos',
        compute='_compute_products_count',
        store=True
    )

    # Campos relacionados de la orden de venta
    sale_delivery_date = fields.Datetime(
        string='Fecha de Entrega',
        related='sale_order_id.delivery_date_first',
        readonly=True,
        store=True
    )

    sale_attended_by = fields.Many2one(
        'hr.employee',
        string='Atendido por',
        related='sale_order_id.attended_by_employee_id',
        readonly=True,
        store=True
    )

    observations = fields.Text(
        string='Observaciones',
        help='Observaciones adicionales sobre la tarea'
    )

    @api.depends('sale_order_line_ids')
    def _compute_products_count(self):
        for task in self:
            task.products_count = len(task.sale_order_line_ids)
