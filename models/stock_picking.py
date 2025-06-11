# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    external_company_id = fields.Many2one(
        'res.partner',
        string='External Company',
        domain="[('is_company','=',True)]"
    )

    def action_open_delivery_slip_email_wizard(self):
        """Open email composition wizard with preview and editing"""
        self.ensure_one()

        # Generate PDF report
        report = self.env.ref('stock.action_report_delivery')
        pdf_content, _ = report._render_qweb_pdf(
            report_ref='stock.report_deliveryslip',
            res_ids=[self.id]
        )

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Delivery_Slip_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'stock.picking',
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        # Prepare recipient list
        recipients = []
        if self.partner_id.email:
            recipients.append(self.partner_id.email)
        if self.external_company_id and self.external_company_id.email:
            recipients.append(self.external_company_id.email)

        if not recipients:
            raise UserError("No email addresses configured for customer or external company.")

        # Email body template
        body = f"""
            <p>Dear Partner,</p>
            <p>Please find attached the delivery slip for order <strong>{self.origin or ''}</strong>.</p>
            <p>Delivery Reference: <strong>{self.name}</strong></p>
            <p>If you have any questions, please don't hesitate to contact us.</p>
            <p>Best regards,<br/>{self.env.user.company_id.name}</p>
        """

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'delivery.slip.email.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('delivery_slip_email.delivery_slip_email_wizard_form').id,
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
                'default_attachment_ids': [(6, 0, [attachment.id])],
                'default_subject': f'Delivery Slip - {self.name}',
                'default_body': body,
                'default_recipient_emails': ','.join(recipients),
            }
        }
