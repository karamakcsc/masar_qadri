import frappe
from frappe.desk.doctype.notification_log.notification_log import make_notification_log

def sales_invoice_notification(doc, method=None):
    notify_sales_return_submission(doc)
    notify_sales_invoice_with_discount(doc)

def notify_sales_return_submission(doc):
    if doc.docstatus == 1 and doc.is_return == 1:
        subject = f"Sales Invoice {doc.name} has been returned from {doc.return_against or 'N/A'}"
        message = f"""
        <b>Order Returned Sales Invoice:</b> {doc.name}<br>
        <b>Customer:</b> {doc.customer}<br>
        <b>Date:</b> {doc.posting_date}<br>
        <b>Total:</b> {frappe.utils.fmt_money(doc.grand_total, currency=doc.currency)}<br>
        <b>Total Qty:</b> {doc.total_qty}<br>
        <b>Return Against:</b> {doc.return_against or 'N/A'}<br>
        <b>Branch:</b> {doc.pos_profile or 'N/A'}<br>
        """

        roles = ["Sales Master Manager"]
        role_holders = frappe.db.get_all(
            "Has Role",
            filters={"role": ["in", roles]},
            pluck="parent"
        )

        emails = frappe.db.get_all(
            "User",
            filters={"name": ["in", role_holders], "enabled": 1},
            pluck="name"
        )

        if not emails:
            frappe.log_error("No recipients found for Sales Return notification", "Sales Return Notification")
            return

        make_notification_log(
            subject=subject,
            for_users=emails,
            type="Alert",
            document_type="Sales Invoice",
            document_name=doc.name,
        )

        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message,
        )
        
def notify_sales_invoice_with_discount(doc):
    if doc.docstatus == 1 and not doc.is_return:
        has_discount = False

        if doc.discount_amount > 0 or doc.additional_discount_percentage > 0:
            has_discount = True

        if not has_discount:
            for item in doc.items:
                if item.discount_amount > 0 or item.discount_percentage > 0:
                    has_discount = True
                    break

        if not has_discount:
            return

        subject = f"Sales Invoice {doc.name} includes a discount"
        message = f"""
        <b>Discounted Sales Invoice:</b> {doc.name}<br>
        <b>Customer:</b> {doc.customer}<br>
        <b>Date:</b> {doc.posting_date}<br>
        <b>Total:</b> {frappe.utils.fmt_money(doc.grand_total, currency=doc.currency)}<br>
        <b>Discount Amount:</b> {frappe.utils.fmt_money(doc.discount_amount or 0, currency=doc.currency)}<br>
        <b>Additional Discount %:</b> {doc.additional_discount_percentage or 0}%<br>
        <b>Branch:</b> {doc.pos_profile or 'N/A'}<br>
        """

        roles = ["Sales Master Manager"]
        role_holders = frappe.db.get_all(
            "Has Role",
            filters={"role": ["in", roles]},
            pluck="parent"
        )

        emails = frappe.db.get_all(
            "User",
            filters={"name": ["in", role_holders], "enabled": 1},
            pluck="name"
        )

        if not emails:
            frappe.log_error("No recipients found for Discounted Sales Invoice notification", "Sales Invoice Discount Notification")
            return

        make_notification_log(
            subject=subject,
            for_users=emails,
            type="Alert",
            document_type="Sales Invoice",
            document_name=doc.name,
        )

        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message,
        )
