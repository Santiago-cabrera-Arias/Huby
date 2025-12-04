import base64
from urllib.parse import urljoin

from odoo import api, fields, models
from odoo.modules.module import get_module_resource


class AccountMove(models.Model):
    _inherit = "account.move"

    x_l10n_mx_edi_qr_text = fields.Char(
        string="URL QR CFDI",
        readonly=True,
        copy=False,
        store=True,
        compute="_compute_x_l10n_mx_edi_qr_text",
        help="URL de verificación del CFDI para el SAT.",
    )

    # --- Helpers de imágenes estáticas para el reporte Huby ---

    def _huby_static_image_base64(self, filename):
        """Retorna la imagen estática del módulo en base64."""
        if not filename:
            return False
        resource_path = get_module_resource("huby_personalize", "static", "src", "img", filename)
        if not resource_path:
            return False
        try:
            with open(resource_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("ascii")
        except OSError:
            return False

    def _huby_invoice_logo(self):
        return self._huby_static_image_base64("logo.png")

    def _huby_invoice_tagline(self):
        return self._huby_static_image_base64("lema.png")

    def _huby_invoice_footer(self):
        return self._huby_static_image_base64("pie_pagina.png")

    # Forzar URL absoluta para el QR estándar de l10n_mx_edi
    def _l10n_mx_edi_get_extra_invoice_report_values(self):
        cfdi_infos = super()._l10n_mx_edi_get_extra_invoice_report_values()
        if not cfdi_infos:
            return cfdi_infos

        barcode_src = cfdi_infos.get("barcode_src")
        if barcode_src:
            base_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url")
                or ""
            )
            if base_url:
                cfdi_infos["barcode_src"] = urljoin(
                    base_url.rstrip("/") + "/", barcode_src.lstrip("/")
                )
        return cfdi_infos

    # --- Cálculo de URL QR CFDI 4.0 (texto) ---

    @api.depends("l10n_mx_edi_cfdi_uuid", "amount_total")
    def _compute_x_l10n_mx_edi_qr_text(self):
        Document = self.env["l10n_mx_edi.document"]
        for move in self:
            if not move.l10n_mx_edi_cfdi_uuid or not move.l10n_mx_edi_cfdi_attachment_id:
                move.x_l10n_mx_edi_qr_text = False
                continue

            try:
                cfdi_raw = (
                    move.with_context(bin_size=False)
                    .l10n_mx_edi_cfdi_attachment_id.raw
                )
                cfdi_infos = Document._decode_cfdi_attachment(cfdi_raw) or {}

                uuid = cfdi_infos.get("uuid") or move.l10n_mx_edi_cfdi_uuid
                emisor = cfdi_infos.get("supplier_rfc")
                receptor = cfdi_infos.get("customer_rfc")
                sello = cfdi_infos.get("sello")

                if not (uuid and emisor and receptor and sello):
                    move.x_l10n_mx_edi_qr_text = False
                    continue

                try:
                    total = float(move.amount_total)
                    total_str = f"{total:.6f}"
                except Exception:
                    move.x_l10n_mx_edi_qr_text = False
                    continue

                fe = sello[-8:]
                url = (
                    "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
                    f"?id={uuid}&re={emisor}&rr={receptor}&tt={total_str}&fe={fe}"
                )
                move.x_l10n_mx_edi_qr_text = url
            except Exception:
                move.x_l10n_mx_edi_qr_text = False

    # --- Monto en letras en español ---

    def _get_amount_total_in_words_es(self):
        """Devuelve el monto total en letras (ES) sin sufijo de moneda.

        El template agrega luego ' M. N.', por eso aquí solo se retorna
        'CINCUENTA PESOS 00/100' (por ejemplo).
        """
        self.ensure_one()
        amount = self.amount_total or 0.0
        amount_i, amount_d = divmod(amount, 1)
        amount_d = round(amount_d, 2)
        amount_d_int = int(round(amount_d * 100, 2))

        lang = self.partner_id.lang or "es_MX"
        words = self.currency_id.with_context(lang=lang).amount_to_text(amount_i)
        return f"{words} {amount_d_int:02d}/100"
