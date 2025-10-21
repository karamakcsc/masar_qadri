import frappe


def validate(self, method):
    create_variant_attribute(self)

def create_variant_attribute(self):
    if self.item_attribute_values:
        for row in self.item_attribute_values:
            if not frappe.db.exists("Variant Attribute", {"attribute": self.name, "attribute_value": row.attribute_value}):
                va = frappe.get_doc({
                    "doctype": "Variant Attribute",
                    "attribute": self.name,
                    "attribute_value": row.attribute_value,
                    "disabled": 0
                })
                va.insert(ignore_permissions=True)
                frappe.db.commit()