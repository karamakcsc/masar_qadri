
import frappe 
from frappe.utils import cstr


def make_variant_item_code(template_item_code, template_item_name, variant):
    """Uses template's item code and abbreviations to make variant's item code"""
    if variant.item_code:
        return
    abbreviations = []
    for attr in variant.attributes:
        item_attribute = frappe.db.sql(
            """SELECT i.numeric_values, v.abbr
            FROM `tabItem Attribute` i 
            LEFT JOIN `tabItem Attribute Value` v ON i.name = v.parent
            WHERE i.name = %(attribute)s AND (v.attribute_value = %(attribute_value)s OR i.numeric_values = 1)""",
            {"attribute": attr.attribute, "attribute_value": attr.attribute_value},
            as_dict=True,
        )
        if not item_attribute:
            continue
        abbr_or_value = (
            cstr(attr.attribute_value) if item_attribute[0].numeric_values else item_attribute[0].abbr
        )
        if abbr_or_value == 'Description': 
            doc = frappe.get_doc('Item' , template_item_code)
            abbr_or_value  = doc.custom_description_code 
            variant.custom_description_code    = doc.custom_description_code 
        abbreviations.append(abbr_or_value)
    
    if abbreviations:
        variant.item_code = "{}".format( "-".join(abbreviations))
        variant.item_name = "{}".format( "-".join(abbreviations))
