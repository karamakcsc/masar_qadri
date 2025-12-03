# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return columns(), data(filters), None

def data(filters):
	conditions = " 1=1 "
	if filters.get("branch"):
		conditions += f" AND tb.warehouse = '{filters.get('branch')}' "
	if filters.get("item_code"):
		conditions += f" AND tb.item_code = '{filters.get('item_code')}' "
	if filters.get("article"):
		conditions += f" AND art.attribute_value LIKE '%{filters.get('article')}%' "


	sql = frappe.db.sql(f"""
			SELECT 
				tb.warehouse AS branch,
				tb.item_code, 
				ti.item_name, 
				ti.custom_description_code AS description, 
				ti.item_group, 
				art.attribute_value AS article,
				col.attribute_value AS color,
				siz.attribute_value AS size,
				tb.valuation_rate AS cost_price, 
				tip.price_list_rate AS selling_price,
				tip.price_list_rate * 0.16 AS tax_amount
			FROM tabBin tb
			INNER JOIN tabItem ti ON tb.item_code = ti.name 
			LEFT JOIN `tabItem Variant Attribute` art 
				ON art.parent = tb.item_code 
			AND art.attribute = 'Article'
			LEFT JOIN `tabItem Variant Attribute` col 
				ON col.parent = tb.item_code 
			AND col.attribute = 'Color'
			LEFT JOIN `tabItem Variant Attribute` siz 
				ON siz.parent = tb.item_code 
			AND siz.attribute = 'Size'
			INNER JOIN `tabItem Price` tip ON tb.item_code = tip.item_code 
			WHERE 
				{conditions}
				AND tip.selling = 1 
				AND ti.has_variants = 0
			GROUP BY tb.warehouse, tb.item_code
		""")

	return sql

def columns():
	return [
		"Branch:Link/Warehouse:200",
		"Item Code:Link/Item:200",
		"Item Name:Data:300",
		"Description:Data:300",
		"Item Group:Data:200",
		"Article:Data:150",
		"Color:Data:150",
		"Size:Data:150",
		"Cost Price:Currency:150",
		"Selling Price:Currency:150",
		"Tax Amount:Currency:150"
	]