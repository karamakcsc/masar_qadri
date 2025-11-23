# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from frappe.model.document import Document


class ItemLabelPrint(Document):
	def validate(self):
		generate_barcode_py(self)
		
	@frappe.whitelist()
	def fetch_items(self):
		filters = {"disabled": 0, "has_variants": 0}

		if self.item_code:
			filters["item_code"] = self.item_code
		if self.item_group:
			filters["item_group"] = self.item_group
		if self.description:
			filters["custom_description_code"] = self.description

		items = frappe.get_all(
			"Item",
			filters=filters,
			fields=[
				"item_code",
				"item_name",
				"item_group",
				"brand",
				"custom_description_code",
				"name as item_name_id",
			]
		)

		for item in items:
			barcodes = frappe.get_all(
				"Item Barcode",
				filters={"parent": item.item_code},
				fields=["barcode"]
			)

			price = frappe.db.get_value(
				"Item Price",
				{"item_code": item.item_code, "selling": 1},
				"price_list_rate"
			)

			attributes = frappe.get_all(
				"Item Variant Attribute",
				filters={"parent": item.item_code},
				fields=["attribute", "attribute_value"]
			)
			attr_map = {a.attribute: a.attribute_value for a in attributes}

			if self.barcode and not any(b["barcode"] == self.barcode for b in barcodes):
				continue
			if self.article and attr_map.get("Article") != self.article:
				continue
			if self.size and attr_map.get("Size") != self.size:
				continue
			if self.style and attr_map.get("Style") != self.style:
				continue
			if self.season and attr_map.get("Season") != self.season:
				continue
			if self.color and attr_map.get("Color") != self.color:
				continue

			self.append("items", {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"barcode": barcodes[0]["barcode"] if barcodes else None,
				"description": item.custom_description_code,
				"item_group": item.item_group,
				"brand": item.brand,
				"price": price,
				"size": attr_map.get("Size"),
				"style": attr_map.get("Style"),
				"season": attr_map.get("Season"),
				"article": attr_map.get("Article"),
				"color": attr_map.get("Color"),
			})

def get_barcode(data, barcode_type):
	barcode_class = barcode.get_barcode_class(barcode_type)
	bar = barcode_class(data, writer=ImageWriter())

	buffer = BytesIO()
	bar.write(buffer, {
		"module_width": 0.4,
		"module_height": 16,
		"quiet_zone": 1.5,
		"font_size": 0,
		"text_distance": 0,
		"background": "white",
		"foreground": "black",
		"write_text": False,
		"dpi": 900,
	})
	
	base64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
	return f"data:image/png;base64,{base64_string}"


@frappe.whitelist()
def generate_barcode_py(self):
	if self.items:
		for item in self.items:
			if item.barcode:
				bar = get_barcode(item.barcode, "code128")
				item.barcode_text = bar