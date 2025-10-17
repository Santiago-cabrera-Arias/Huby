# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProhibitedCustomerWords(models.Model):
    _name = 'prohibited.customer.words'
    _description = 'Palabras prohibidas para nombres de clientes'

    word = fields.Char(
        string='Palabra',
        required=True,
        help='Palabra que no se permite en nombres de nuevos clientes si ya existe un cliente con esta palabra'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está activo, la validación se aplicará para esta palabra'
    )

    @api.constrains('word')
    def _check_word_unique(self):
        """Validar que la palabra no se repita en registros activos"""
        for record in self:
            if record.word:
                existing = self.search([
                    ('word', '=ilike', record.word),
                    ('id', '!=', record.id),
                    ('active', '=', True)
                ])
                if existing:
                    raise ValidationError(
                        f'La palabra "{record.word}" ya está registrada como palabra prohibida.'
                    )
