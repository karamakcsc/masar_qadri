# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VariantAttribute(Document):
	pass

@frappe.whitelist()
def sync_attributes():
	attributes_sql = frappe.db.sql("""
		SELECT parent, attribute_value
		FROM `tabItem Attribute Value`
		WHERE parent NOT IN ('Description', 'Fabric', 'Supplier')
	""", as_dict=True)

	for attr in attributes_sql:
		existing = frappe.db.exists("Variant Attribute", {
			"attribute": attr.parent,
			"attribute_value": attr.attribute_value
		})
		if not existing:
			new_va = frappe.new_doc("Variant Attribute")
			new_va.attribute = attr.parent
			new_va.attribute_value = attr.attribute_value
			new_va.disabled = 0
			new_va.insert()