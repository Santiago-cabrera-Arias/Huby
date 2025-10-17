# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    sale_delivery_date = fields.Datetime(
        string="Fecha de Entrega",
        related="sale_order_id.delivery_date_first",
        store=True,
        readonly=True,
    )

    sale_attended_by = fields.Many2one(
        "hr.employee",
        string="Atendido por",
        related="sale_order_id.attended_by_employee_id",
        store=True,
        readonly=True,
    )
