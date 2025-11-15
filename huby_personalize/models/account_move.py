# -*- coding: utf-8 -*-
"""Account Move helpers for Huby reports."""
import base64
from urllib.parse import urljoin

# pylint: disable=import-error
from odoo import models
from odoo.modules.module import get_module_resource


class AccountMove(models.Model):
    _inherit = "account.move"

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

    def _huby_invoice_logo(self):
        return self._huby_static_image_base64('logo.png')

    def _huby_invoice_tagline(self):
        return self._huby_static_image_base64('lema.png')

    def _huby_invoice_footer(self):
        return self._huby_static_image_base64('pie_pagina.png')

    def _l10n_mx_edi_get_extra_invoice_report_values(self):
        """Ensure barcode sources use the absolute URL so wkhtmltopdf can fetch them."""
        cfdi_infos = super()._l10n_mx_edi_get_extra_invoice_report_values()
        if not cfdi_infos:
            return cfdi_infos

        barcode_src = cfdi_infos.get('barcode_src')
        if barcode_src:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
            if base_url:
                cfdi_infos['barcode_src'] = urljoin(base_url.rstrip('/') + '/', barcode_src.lstrip('/'))

        return cfdi_infos
