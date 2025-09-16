# -*- coding: utf-8 -*-
# File: custom/addons/delivery_slip_email/models/stock_picking.py
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # --- Extra fields (kept from your original module)
    scheduled_date = fields.Datetime(string='Scheduled Date')
    commitment_date = fields.Date(string='Commitment Date')
    client_order_ref = fields.Char(string='Client Order Reference')
    commitment_delivery_date = fields.Date(string='Commitment Delivery Date')
    measurement_date = fields.Date(string='Measurement Date')

    external_company_id = fields.Many2one(
        'res.partner',
        string='External Company',
        domain="[('is_company','=',True)]"
    )

    # -------------------------------------------------------------------------
    # This is the method referenced by your button in the view.
    # The view expects action_open_delivery_slip_email_wizard to exist.
    # -------------------------------------------------------------------------
    # def action_open_delivery_slip_email_wizard(self):
    #     """
    #     Open the email composition wizard preloaded with:
    #       - Delivery slip PDF (always)
    #       - Posted invoice PDFs (if any)
    #     Returns an act_window to open the transient wizard form.
    #     """
    #     self.ensure_one()
    #
    #     attachments = []  # 📌 collect ids of created ir.attachment records
    #
    #     # ----------------------------
    #     # 1) Delivery Slip PDF
    #     # ----------------------------
    #     report = self.env.ref('stock.action_report_delivery')  # standard delivery report
    #     # ✅ Odoo 17: use ir.actions.report._render_qweb_pdf(report_name, ids)
    #     pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
    #         report.report_name, [self.id]
    #     )  # <-- IMPORTANT fixed line
    #     attachment = self.env['ir.attachment'].create({
    #         'name': f'Delivery_Slip_{self.name}.pdf',
    #         'type': 'binary',
    #         'datas': base64.b64encode(pdf_content),  # store binary data base64-encoded
    #         'res_model': 'stock.picking',
    #         'res_id': self.id,
    #         'mimetype': 'application/pdf',
    #     })
    #     attachments.append(attachment.id)
    #
    #     # ----------------------------
    #     # 2) Invoice PDFs (if exist & posted)
    #     # ----------------------------
    #     # If the picking is linked to a sale order and that sale has posted invoices,
    #     # render and attach them as well.
    #     if self.sale_id and self.sale_id.invoice_ids:
    #         # filter only posted invoices
    #         posted_invoices = self.sale_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
    #         report_invoice = None
    #         # Protect against missing report xmlid
    #         try:
    #             report_invoice = self.env.ref('account.account_invoices')
    #         except Exception:
    #             report_invoice = None
    #
    #         if report_invoice:
    #             for invoice in posted_invoices:
    #                 pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
    #                     report_invoice.report_name, [invoice.id]
    #                 )  # <-- IMPORTANT fixed line for invoice rendering
    #                 inv_attachment = self.env['ir.attachment'].create({
    #                     'name': f'Invoice_{invoice.name}.pdf',
    #                     'type': 'binary',
    #                     'datas': base64.b64encode(pdf_content),
    #                     'res_model': 'account.move',
    #                     'res_id': invoice.id,
    #                     'mimetype': 'application/pdf',
    #                 })
    #                 attachments.append(inv_attachment.id)
    #         else:
    #             _logger.debug("account.account_invoices report not found, skipping invoice attachments.")
    #
    #     # ----------------------------
    #     # 3) Prepare recipient emails
    #     # ----------------------------
    #     recipients = []
    #     if self.partner_id and self.partner_id.email:
    #         recipients.append(self.partner_id.email)
    #     if self.external_company_id and self.external_company_id.email:
    #         recipients.append(self.external_company_id.email)
    #
    #     if not recipients:
    #         raise UserError("No email addresses configured for customer or external company.")
    #
    #     # ----------------------------
    #     # 4) Prepare body and open wizard
    #     # ----------------------------
    #     body = f"""
    #         <p>Dear {self.partner_id.name or 'Partner'},</p>
    #         <p>Please find attached the delivery slip and related documents for order <strong>{self.origin or ''}</strong>.</p>
    #         <p>Delivery Reference: <strong>{self.name}</strong></p>
    #         <p>Regards,<br/>{(self.env.user.company_id and self.env.user.company_id.name) or ''}</p>
    #     """
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'delivery.slip.email.wizard',  # your transient model
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('delivery_slip_email.delivery_slip_email_wizard_form').id,
    #         'target': 'new',
    #         'context': {
    #             'default_picking_id': self.id,
    #             'default_attachment_ids': [(6, 0, attachments)],  # preload attachments into wizard
    #             'default_subject': f'Delivery Slip - {self.name}',
    #             'default_body': body,
    #             'default_recipient_emails': ','.join(recipients),
    #         }
    #     }




    def action_open_delivery_slip_email_wizard(self):
        """
        Open the email composition wizard preloaded with:
          - Delivery slip PDF (always)
          - No invoice PDFs (user can attach manually if needed)
        """
        self.ensure_one()

        attachments = []  # collect ids of created ir.attachment records

        # ----------------------------
        # 1) Delivery Slip PDF (always)
        # ----------------------------
        report = self.env.ref('stock.action_report_delivery')
        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            report.report_name, [self.id]
        )
        attachment = self.env['ir.attachment'].create({
            'name': f'Delivery_Slip_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'stock.picking',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        attachments.append(attachment.id)

        # ----------------------------
        # 2) Prepare recipient emails
        # ----------------------------
        recipients = []
        if self.partner_id and self.partner_id.email:
            recipients.append(self.partner_id.email)
        if self.external_company_id and self.external_company_id.email:
            recipients.append(self.external_company_id.email)

        if not recipients:
            raise UserError("No email addresses configured for customer or external company.")

        # ----------------------------
        # 3) Prepare body and open wizard
        # ----------------------------
        body = f"""
            <p>Dear {self.partner_id.name or 'Partner'},</p>
            <p>Please find attached the delivery slip for order <strong>{self.origin or ''}</strong>.</p>
            <p>Delivery Reference: <strong>{self.name}</strong></p>
            <p>Regards,<br/>{(self.env.user.company_id and self.env.user.company_id.name) or ''}</p>
        """

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.slip.email.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('delivery_slip_email.delivery_slip_email_wizard_form').id,
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'default_attachment_ids': [(6, 0, attachments)],  # preload only delivery slip
                'default_subject': f'Delivery Slip - {self.name}',
                'default_body': body,
                'default_recipient_emails': ','.join(recipients),
            }
        }

    # -------------------------------------------------------------------------
    # Optional helper: a direct send (kept for backward compatibility if you use it)
    # This method sends via a mail template (if you use it elsewhere).
    # -------------------------------------------------------------------------
    def action_send_delivery_email(self):
        for picking in self:
            if not picking.partner_id.email:
                raise UserError(_("Delivery address has no email."))

            # Generate Delivery Slip PDF once
            report = self.env.ref('stock.action_report_delivery')
            pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
                report.report_name, [picking.id]
            )

            # Create a single attachment (in-memory, not stored permanently)
            attachment = self.env['ir.attachment'].create({
                'name': f'Delivery Slip - {picking.name}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'stock.picking',
                'res_id': picking.id,
                'mimetype': 'application/pdf',
            })

            # Prepare mail template dynamically
            mail_values = {
                'subject': _('Delivery Slip - %s') % picking.name,
                'body_html': _('<p>Dear %s,</p><p>Please find attached your delivery slip.</p>') % picking.partner_id.name,
                'email_to': picking.partner_id.email,
                'attachment_ids': [(6, 0, [attachment.id])],  # attach once
            }

            # Send email
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()

        return True

class AccountMove(models.Model):
    _inherit = 'account.move'

    origin = fields.Char(string='Source Document')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    commitment_date = fields.Date(string='Commitment Date')
    client_order_ref = fields.Char(string='Client Order Reference')
