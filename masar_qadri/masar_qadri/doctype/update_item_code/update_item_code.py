# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UpdateItemCode(Document):
	@frappe.whitelist()
	def enqueue_update(queue="long", timeout=3000):
		frappe.enqueue(
        "update_name",
        queue=queue,
        timeout=timeout
    )
    return "Enqueued job to update item names and codes."
 
	def update_name():
		items_sql = frappe.db.sql("""
            SELECT name, item_code
			FROM tabItem
		""", as_dict=True)
		try:
			if items_sql:
				for row in items_sql:
					if "\n" in row.name or "\r" in row.name:
						new_name = re.sub(r'[\r\n]+', '', row.name)
						frappe.rename_doc("Item", row.name, new_name)
					if "\n" in row.item_code or "\r" in row.item_code:
						new_code = re.sub(r'[\r\n]+', '', row.item_code)
						frappe.db.set_value("Item", row.name, "item_code", new_code)
			frappe.msgprint("Updated Items Successfully")
		except Exception as e:
			frappe.throw(f"Error Updating Item: {e}")