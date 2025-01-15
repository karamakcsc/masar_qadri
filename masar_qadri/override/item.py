
import frappe 
from frappe import _
from frappe.utils import cstr
import json
from erpnext.controllers.item_variant import get_variant , generate_keyed_value_combinations , copy_attributes_to_variant
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



@frappe.whitelist()
def enqueue_multiple_variant_creation(item, args, use_template_image=False):
	use_template_image = frappe.parse_json(use_template_image)
	# There can be innumerable attribute combinations, enqueue
	if isinstance(args, str):
		variants = json.loads(args)
	total_variants = 1
	for key in variants:
		total_variants *= len(variants[key])
	if total_variants >= 600:
		frappe.throw(_("Please do not create more than 500 items at a time"))
		return
	if total_variants < 10:
		return create_multiple_variants(item, args, use_template_image)
	else:
		frappe.enqueue(
			"masar_qadri.override.item.create_multiple_variants",
			item=item,
			args=args,
			use_template_image=use_template_image,
			now=frappe.flags.in_test,
		)
		return "queued"



def create_multiple_variants(item, args, use_template_image=False):
	count = 0
	if isinstance(args, str):
		args = json.loads(args)

	template_item = frappe.get_doc("Item", item)
	args_set = generate_keyed_value_combinations(args)

	for attribute_values in args_set:
		if not get_variant(item, args=attribute_values):
			variant = create_variant(item, attribute_values)
			if use_template_image and template_item.image:
				variant.image = template_item.image
			variant.save()
			count += 1

	return count



@frappe.whitelist()
def create_variant(item, args, use_template_image=False):
	use_template_image = frappe.parse_json(use_template_image)
	if isinstance(args, str):
		args = json.loads(args)

	template = frappe.get_doc("Item", item)
	variant = frappe.new_doc("Item")
	variant.variant_based_on = "Item Attribute"
	variant_attributes = []

	for d in template.attributes:
		variant_attributes.append({"attribute": d.attribute, "attribute_value": args.get(d.attribute)})

	variant.set("attributes", variant_attributes)
	copy_attributes_to_variant(template, variant)

	if use_template_image and template.image:
		variant.image = template.image

	make_variant_item_code(template.item_code, template.item_name, variant)

	return variant