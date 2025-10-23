import frappe
from frappe.desk.doctype.notification_log.notification_log import make_notification_logs


def pos_opening_shift_notification(doc, method=None):
    if doc.docstatus != 1:
        return

    subject = f"POS Opening Shift {doc.name} Started - {doc.pos_profile or 'N/A'}"

    payments = ""
    if getattr(doc, "balance_details", None):
        payments = "<br><b>Opening Balances:</b><br>"
        for d in doc.balance_details:
            payments += f"- {d.mode_of_payment}: {d.amount or 0}<br>"

    message = f"""
    <b>POS Opening Shift:</b> {doc.name}<br>
    <b>POS Profile:</b> {doc.pos_profile or 'N/A'}<br>
    <b>Opened By:</b> {doc.user or doc.owner}<br>
    <b>Company:</b> {doc.company or 'N/A'}<br>
    <b>Opening Date:</b> {doc.period_start_date or doc.posting_date or 'N/A'}<br>
    <b>Float Cash:</b> {doc.float_cash or 0}<br>
    {payments}
    <hr>
    <i>This is an automated notification for POS Opening Shift creation.</i>
    """

    recipients = _get_pos_shift_recipients()
    if not recipients:
        frappe.log_error(f"No recipients found for POS Opening Shift {doc.name}", "POS Opening Shift Notification")
        return

    make_notification_logs(
        subject=subject,
        for_users=recipients,
        type="Alert",
        document_type="POS Opening Shift",
        document_name=doc.name,
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
    )


def pos_closing_shift_notification(doc, method=None):
    if doc.docstatus != 1:
        return

    subject = f"POS Closing Shift {doc.name} Completed - {doc.pos_profile or 'N/A'}"

    total_invoices = len(doc.pos_transactions or [])
    total_amount = doc.grand_total or 0.0
    total_qty = doc.total_quantity or 0.0
    taxes = sum([t.get("amount", 0) for t in (doc.taxes or [])])
    difference = sum([d.get("difference", 0) for d in (doc.payment_reconciliation or [])])

    payments = ""
    if getattr(doc, "payment_reconciliation", None):
        payments = "<br><b>Payment Reconciliation:</b><br>"
        for d in doc.payment_reconciliation:
            payments += f"- {d.mode_of_payment}: Expected {d.expected_amount}, Closed {d.closing_amount}, Diff {d.difference}<br>"

    message = f"""
    <b>POS Closing Shift:</b> {doc.name}<br>
    <b>POS Profile:</b> {doc.pos_profile or 'N/A'}<br>
    <b>Closed By:</b> {doc.user or doc.owner}<br>
    <b>Company:</b> {doc.company or 'N/A'}<br>
    <b>Start:</b> {doc.period_start_date or 'N/A'}<br>
    <b>End:</b> {doc.period_end_date or 'N/A'}<br>
    <b>Total Invoices:</b> {total_invoices}<br>
    <b>Total Qty:</b> {total_qty}<br>
    <b>Net Total:</b> {doc.net_total or 0:.2f}<br>
    <b>Taxes:</b> {taxes:.2f}<br>
    <b>Grand Total:</b> {total_amount:.2f}<br>
    <b>Difference:</b> {difference:.2f}<br>
    <b>Cash Float:</b> {doc.float_cash or 0}<br>
    <b>Linked Opening Shift:</b> {doc.pos_opening_shift or 'N/A'}<br>
    {payments}
    <hr>
    <i>This is an automated notification for POS Closing Shift submission.</i>
    """

    recipients = _get_pos_shift_recipients()
    if not recipients:
        frappe.log_error(f"No recipients found for POS Closing Shift {doc.name}", "POS Closing Shift Notification")
        return

    make_notification_logs(
        subject=subject,
        for_users=recipients,
        type="Alert",
        document_type="POS Closing Shift",
        document_name=doc.name,
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
    )


def _get_pos_shift_recipients():
    recipients = []

    role_recipients = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["Sales Master Manager", "Accounts Manager"]]},
        pluck="parent"
    )
    recipients += role_recipients

    return list(set(recipients))
