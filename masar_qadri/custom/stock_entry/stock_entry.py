import frappe
# from frappe.desk.doctype.notification_log.notification_log import make_notification_log


def on_submit(self, method):
    validate_original_se(self)
    set_se_transfer_status(self, "Complete")
    # notify_stock_entry_transfer(self)
def on_cancel(self, method):
    set_se_transfer_status(self, "Pending")

def set_se_transfer_status(self, status):
    if self.outgoing_stock_entry:
        parent_se = frappe.get_value("Stock Entry", self.outgoing_stock_entry, "add_to_transit")

        if parent_se:
            frappe.db.set_value("Stock Entry", self.outgoing_stock_entry, "custom_transfer_status", status)

def validate_original_se(self):
    if not self.outgoing_stock_entry:
        return

    original_se = frappe.get_doc("Stock Entry", self.outgoing_stock_entry)
    original_items = {i.item_code: i.qty for i in original_se.items}

    previous_entries = frappe.get_all(
        "Stock Entry",
        filters={
            "docstatus": 1,
            "outgoing_stock_entry": self.outgoing_stock_entry,
            "name": ["!=", self.name],
        },
        fields=["name"]
    )

    prev_total = {}
    if previous_entries:
        for entry in previous_entries:
            se = frappe.get_doc("Stock Entry", entry.name)
            for it in se.items:
                prev_total[it.item_code] = prev_total.get(it.item_code, 0) + it.qty

    for item in self.items:
        if item.item_code not in original_items:
            frappe.throw(
                f"Item <b>{item.item_code}</b> in <b> row {item.idx} </b> does not exist in the original Stock Entry."
            )

        original_qty = original_items[item.item_code]
        previously_used = prev_total.get(item.item_code, 0)
        remaining_allowed = original_qty - previously_used

        if item.qty > remaining_allowed:
            frappe.throw(
                f"Quantity for item <b>{item.item_code}</b> in <b> row {item.idx} </b> exceeds remaining allowed quantity.<br>"
                f"Original Qty: <b>{original_qty}</b><br>"
                f"Used in previous Check In entries: <b>{previously_used}</b><br>"
                f"Remaining allowed: <b>{remaining_allowed}</b>"
            )

# def notify_stock_entry_transfer(doc):
#     """Notify target warehouse recipients and role-based users when stock is transferred"""
#     if doc.docstatus != 1 or doc.stock_entry_type != "Material Transfer" or doc.outgoing_stock_entry:
#         return

#     subject = f"Stock Transfer {doc.name}: {doc.from_warehouse or 'N/A'} → {doc.to_warehouse or 'N/A'}"
#     message = f"""
#     <b>Stock Transfer:</b> {doc.name}<br>
#     <b>From Warehouse:</b> {doc.from_warehouse or 'N/A'}<br>
#     <b>To Warehouse:</b> {doc.to_warehouse or 'N/A'}<br>
#     <b>Date:</b> {doc.posting_date}<br>
#     <b>Total Qty:</b> {doc.total_outgoing_qty or 0}<br>
#     <b>Company:</b> {doc.company or 'N/A'}<br>
#     <b>Transferred By:</b> {doc.owner or 'System'}<br>
#     """

#     recipients = frappe.db.get_all(
#         "Warehouse",
#         filters={"name": doc.to_warehouse},
#         pluck="custom_user"
#     )

#     role_recipients = frappe.db.get_all(
#         "Has Role",
#         filters={"role": ["in", ["Stock Manager"]]},
#         pluck="parent"
#     )

#     all_recipients = list(set((recipients or []) + (role_recipients or [])))

#     if not all_recipients:
#         frappe.log_error(
#             f"No notification recipients found for warehouse {doc.to_warehouse}",
#             "Stock Entry Transfer Notification"
#         )
#         return

#     make_notification_log(
#         subject=subject,
#         for_users=all_recipients,
#         type="Alert",
#         document_type="Stock Entry",
#         document_name=doc.name,
#     )

#     frappe.sendmail(
#         recipients=all_recipients,
#         subject=subject,
#         message=message,
#     )

