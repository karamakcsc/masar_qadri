# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UpdateItemAttribute(Document):
	def validate(self):
		self.validate_new_attributes()
	def on_submit(self):
		self.update_item_attributes()

	@frappe.whitelist()
	def get_item_attribute(self):
		if not self.item:
			frappe.throw("Please select an Item")
		attributes_sql = frappe.db.sql("""
					SELECT attribute, attribute_value
					FROM `tabItem Variant Attribute`
					WHERE parent = %s AND attribute NOT IN ('Description', 'Fabric', 'Supplier')
				""", (self.item,), as_dict=True)
		if not attributes_sql:
			frappe.throw("No attributes found for the selected Item Code")

		return attributes_sql

	def validate_new_attributes(self):
		if not self.update_attributes:
			frappe.throw("Please add at least one new attribute to update")

		for attr in self.update_attributes:
			if not attr.new_attribute_value or not attr.attribute_value:
				frappe.throw("Please fill all the new attribute fields before submitting")
			if attr.attribute_value not in (self.item or self.item_name):
				frappe.throw(f"Attribute Value '{attr.attribute_value}' does not exist for the selected Item")
    
	def update_item_attributes(self):
		for attr in self.update_attributes:
			if attr.current_attribute_value == attr.attribute_value:
				continue
			variant_attr_name = frappe.db.get_value(
				"Item Variant Attribute",
				{"parent": self.item, "attribute": attr.attribute, "attribute_value": attr.current_attribute_value},
				"name"
			)
			if variant_attr_name:
				frappe.db.set_value("Item Variant Attribute", variant_attr_name, "attribute_value", attr.attribute_value)
		frappe.db.commit()
		frappe.msgprint(f"Item attributes for item {self.item} updated successfully.", alert=True, indicator='green')
