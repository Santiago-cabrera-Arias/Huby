# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Validar que no se cree un cliente con una palabra prohibida al inicio del nombre
        si ya existe un cliente con esa palabra al inicio.
        """
        # Obtener todas las palabras prohibidas activas una sola vez
        prohibited_words = self.env['prohibited.customer.words'].search([
            ('active', '=', True)
        ])

        for vals in vals_list:
            partner_name = vals.get('name', '').lower().strip()

            if partner_name:
                for prohibited in prohibited_words:
                    word = prohibited.word.lower().strip()

                    # Verificar si el nombre del partner comienza con la palabra prohibida
                    if partner_name.startswith(word):
                        # Buscar si ya existe algún cliente que comience con esta palabra
                        existing_customer = self.search([
                            ('name', '=ilike', f'{word}%')
                        ], limit=1)

                        if existing_customer:
                            raise ValidationError(
                                f'No se puede crear el cliente con el nombre "{vals.get("name")}" '
                                f'porque ya existe un cliente que comienza con la palabra "{prohibited.word}": '
                                f'"{existing_customer.name}".'
                            )

        return super(ResPartner, self).create(vals_list)
