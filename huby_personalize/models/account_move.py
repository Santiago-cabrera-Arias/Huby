# -*- coding: utf-8 -*-
"""Account Move helpers for Huby reports."""
import base64

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
