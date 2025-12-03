# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return columns(), data(filters), None

def data(filters):
	conditions = " 1=1 "
	if filters.get("item_code"):
		conditions += f" AND tb.item_code = '{filters.get('item_code')}' "
	if filters.get("article"):
		conditions += f" AND art.attribute_value LIKE '%{filters.get('article')}%' "

	sql = frappe.db.sql(f"""
			SELECT 
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
			GROUP BY tb.item_code
		""", as_dict=1)

	result = []
	for row in sql:
		supplier = extract_supplier(row.get('item_name', ''))
		
		if filters.get("supplier") and filters.get("supplier").upper() not in supplier.upper():
			continue
		
		result.append([
			supplier,
			row.get('item_code'),
			row.get('item_name'),
			row.get('description'),
			row.get('item_group'),
			row.get('article'),
			row.get('color'),
			row.get('size'),
			row.get('cost_price'),
			row.get('selling_price'),
			row.get('tax_amount')
		])
	
	return result

def extract_supplier(item_name):
	try:
		parts = item_name.split('-')
		if len(parts) >= 2:
			last_part = parts[-1]
			supplier = last_part.split('/')[0]
			return supplier.strip()
	except:
		pass
	
	return "Unknown"

def columns():
	return [
		"Supplier:Data:200",
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