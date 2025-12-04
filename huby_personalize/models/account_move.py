from io import BytesIO
import base64

from odoo import api, fields, models

try:
    import qrcode
except Exception:  # ImportError and any env-specific issues
    qrcode = None


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_mx_edi_qr_code = fields.Binary(
        string="QR CFDI",
        readonly=True,
        copy=False,
        store=True,
        compute="_compute_l10n_mx_edi_qr_code",
        help="Imagen del código QR del CFDI.",
    )

    @api.depends("l10n_mx_edi_cfdi_attachment_id", "l10n_mx_edi_cfdi_sat_state", "amount_total")
    def _compute_l10n_mx_edi_qr_code(self):
        Document = self.env["l10n_mx_edi.document"]
        for move in self:
            if not move.l10n_mx_edi_cfdi_attachment_id or move.l10n_mx_edi_cfdi_sat_state != "valid":
                move.l10n_mx_edi_qr_code = False
                continue

            if qrcode is None:
                move.l10n_mx_edi_qr_code = False
                continue

            try:
                cfdi_raw = (
                    move.with_context(bin_size=False)
                    .l10n_mx_edi_cfdi_attachment_id.raw
                )
                cfdi_infos = Document._decode_cfdi_attachment(cfdi_raw) or {}

                uuid = cfdi_infos.get("uuid")
                emisor = cfdi_infos.get("supplier_rfc")
                receptor = cfdi_infos.get("customer_rfc")
                sello = cfdi_infos.get("sello")

                if not (uuid and emisor and receptor and sello):
                    move.l10n_mx_edi_qr_code = False
                    continue

                try:
                    total = float(move.amount_total)
                    total_str = f"{total:.6f}"
                except Exception:
                    move.l10n_mx_edi_qr_code = False
                    continue

                fe = sello[-8:]
                url = (
                    "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
                    f"?id={uuid}&re={emisor}&rr={receptor}&tt={total_str}&fe={fe}"
                )

                buffer = BytesIO()
                img = qrcode.make(url)
                img.save(buffer, format="PNG")
                move.l10n_mx_edi_qr_code = base64.b64encode(buffer.getvalue())
            except Exception:
                move.l10n_mx_edi_qr_code = False

