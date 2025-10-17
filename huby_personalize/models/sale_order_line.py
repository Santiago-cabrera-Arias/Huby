# -*- coding: utf-8 -*-
from odoo import models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task(self, project):
        """
        Override para prevenir la creación de múltiples tareas de la misma orden.
        Solo crea UNA tarea por orden con todos los productos agrupados.
        """
        self.ensure_one()

        # Buscar si ya existe una tarea para esta orden y proyecto
        existing_task = self.env['project.task'].search([
            ('sale_order_id', '=', self.order_id.id),
            ('project_id', '=', project.id),
        ], limit=1)

        if existing_task:
            # Si ya existe una tarea, simplemente asignar esta línea a esa tarea
            self.task_id = existing_task

            # Actualizar la descripción para incluir este producto
            self._update_grouped_task_description(existing_task)

            return existing_task
        else:
            # Si no existe, crear la tarea agrupada
            return self._create_grouped_task(project)

    def _create_grouped_task(self, project):
        """
        Crea una tarea agrupada con información de todos los productos de la orden.
        """
        # Obtener todas las líneas de la misma orden que crearán tareas en este proyecto
        all_lines = self.env['sale.order.line'].search([
            ('order_id', '=', self.order_id.id),
            ('product_id.service_tracking', '=', 'task_in_project'),
            ('state', '=', 'sale'),
        ])

        # Nombre de la tarea usando el project_name de la orden
        if self.order_id.project_name:
            task_name = f"{self.order_id.name} - {self.order_id.project_name}"
        else:
            task_name = self.order_id.name

        # Calcular horas totales
        total_hours = sum(line._convert_qty_company_hours(self.company_id)
                         for line in all_lines
                         if line.product_id.service_type not in ['milestones', 'manual'])

        # Crear la tarea (sin descripción HTML, se verá en la pestaña Productos)
        task_values = {
            'name': task_name,
            'allocated_hours': total_hours,
            'partner_id': self.order_id.partner_id.id,
            'description': False,  # No agregar descripción HTML
            'project_id': project.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'company_id': project.company_id.id,
            'user_ids': False,
        }

        task = self.env['project.task'].sudo().create(task_values)
        self.task_id = task

        # Mensaje en la tarea
        task_msg = _("Esta tarea agrupa todos los productos de la orden: %(order_link)s",
            order_link=self.order_id._get_html_link(),
        )
        task.message_post(body=task_msg)

        return task

    def _update_grouped_task_description(self, task):
        """
        Actualiza las horas de la tarea agrupada cuando se agrega una nueva línea.
        """
        # Obtener todas las líneas asignadas a esta tarea
        all_lines = self.env['sale.order.line'].search([
            ('task_id', '=', task.id),
        ])

        # Recalcular horas totales
        total_hours = sum(line._convert_qty_company_hours(self.company_id)
                         for line in all_lines
                         if line.product_id.service_type not in ['milestones', 'manual'])

        # Actualizar solo las horas (los productos se ven en la pestaña Productos)
        task.write({
            'allocated_hours': total_hours,
        })

