# -*- coding: utf-8 -*-
{
    'name': 'Huby Personalize',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Personalización para agregar nombre de proyecto en cotizaciones',
    'description': """
        Este módulo agrega un campo de nombre de proyecto en las cotizaciones
        - Campo en formulario de cotización debajo del cliente
        - Columna visible en la vista tree
        - Filtro de búsqueda por nombre de proyecto
        - CRUD para gestionar palabras prohibidas en nombres de clientes
        - Validación para evitar crear clientes duplicados con palabras prohibidas
        - Campos de fechas de entrega con control de modificación
        - Agrupación de tareas de proyectos: une múltiples productos de una orden en una sola tarea
    """,
    'author': 'Huby',
    'depends': ['sale', 'sales_team', 'hr', 'sale_project'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/prohibited_customer_words_views.xml',
        'views/project_task_views.xml',
        'report/project_task_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
