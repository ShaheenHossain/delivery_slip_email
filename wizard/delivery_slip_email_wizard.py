# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class DeliverySlipEmailWizard(models.TransientModel):
    _name = 'delivery.slip.email.wizard'
    _description = 'Delivery Slip Email Wizard'

    picking_id = fields.Many2one('stock.picking', string='Delivery Order')
    subject = fields.Char(string='Subject', required=True)
    body = fields.Html(string='Email Body')
    recipient_emails = fields.Char(string='Recipients', readonly=True)

    # Existing attachments
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments'
    )

    # Uploaded files from PC (new relation table)
    upload_files = fields.Many2many(
        'ir.attachment',
        'delivery_slip_upload_files_rel',  # Unique relation table
        'wizard_id', 'attachment_id',
        string="Upload PDF Files"
    )

    def action_send_email(self):
        self.ensure_one()

        try:
            # Combine existing attachments + uploaded files
            all_attachment_ids = self.attachment_ids.ids + self.upload_files.ids

            if not self.recipient_emails:
                raise UserError("Delivery address has no email.")

            mail_values = {
                'subject': self.subject,
                'body_html': self.body,
                'email_from': self.env.user.email,
                'email_to': self.recipient_emails,
                'model': 'stock.picking',
                'res_id': self.picking_id.id,
                'attachment_ids': [(6, 0, all_attachment_ids)],
            }

            # Create and send email
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send(auto_commit=True)

            if mail.state != 'sent':
                raise UserError("Email failed to send - please check mail logs")

            # Log in chatter
            attachments_for_chatter = self.env['ir.attachment'].browse(all_attachment_ids)
            self.picking_id.message_post(
                body=f"Delivery slip sent to: {self.recipient_emails}",
                subject="Delivery Slip Sent",
                attachments=[(att.name, att.datas) for att in attachments_for_chatter]
            )

            # ✅ Close the wizard after success
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            raise UserError(f"Failed to send email: {str(e)}")

