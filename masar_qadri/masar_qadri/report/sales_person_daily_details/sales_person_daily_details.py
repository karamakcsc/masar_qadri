# Copyright (c) 2025, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _, qb
from frappe.query_builder import Criterion
from erpnext import get_company_currency


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	entries = get_entries(filters)
	item_details = get_item_details()
	data = []

	company_currency = get_company_currency(filters.get("company"))

	total_qty = 0
	total_amount = 0
	total_transactions = 0

	for d in entries:
		if d.stock_qty > 0 or filters.get("show_return_entries", 0):
			qty = d.stock_qty
			amount = d.amount
			upt = qty / 1  # each Sales Invoice = one transaction
			atv = amount / qty if qty else 0

			data.append([
				d.name,
				d.pos_profile,
				d.sales_person,
				d.customer,
				d.warehouse,
				d.posting_date,
				d.item_code,
				d.item_name,
				item_details.get(d.item_code, {}).get("item_group"),
				item_details.get(d.item_code, {}).get("article"),
				item_details.get(d.item_code, {}).get("description_code"),
				qty,
				amount,
				upt,
				atv,
				company_currency,
			])

			total_qty += qty
			total_amount += amount
			total_transactions += 1

	# Add average row
	if total_transactions > 0:
		avg_upt = total_qty / total_transactions
		avg_atv = total_amount / total_qty if total_qty else 0

		data.append([
			"",
			"",
			"",
			"",
			"",
			"",
			"",
			"<b>Average</b>",
			"",
			"",
			"",
			"",
			"",
			avg_upt,
			avg_atv,
			"",
		])

	return columns, data


def get_columns(filters):
	return [
		{
			"label": _("Sales Invoice"),
			"options": "Sales Invoice",
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("POS Profile"),
			"options": "POS Profile",
			"fieldname": "pos_profile",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Sales Person"),
			"options": "Sales Person",
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"width": 120,
		},
		{
			"label": _("Customer"),
			"options": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"width": 160,
		},
		{
			"label": _("Warehouse"),
			"options": "Warehouse",
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Item Code"),
			"options": "Item",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"width": 140,
			"hidden": 1,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"label": _("Item Group"),
			"options": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Link",
			"width": 140,
		},
		{"label": _("Article"), "fieldname": "article", "fieldtype": "Data", "width": 120},
		{"label": _("Description Code"), "fieldname": "description_code", "fieldtype": "Data", "width": 140},
		{"label": _("Invoice Total Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 120},
		{
			"label": _("Amount"),
			"options": "currency",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		{"label": _("UPT"), "fieldname": "upt", "fieldtype": "Float", "width": 100},
		{"label": _("ATV"), "fieldname": "atv", "fieldtype": "Currency", "width": 120},
		{
			"label": _("Currency"),
			"options": "Currency",
			"fieldname": "currency",
			"fieldtype": "Link",
			"hidden": 1,
		},
	]


def get_entries(filters):
	date_field = "posting_date"

	conditions, values = get_conditions(filters, date_field)

	entries = frappe.db.sql(
		f"""
		SELECT
			tsi.name,
			tsi.customer,
			tsi.posting_date AS posting_date,
			tsi.pos_profile,
			tsii.item_code,
			tsii.item_name,
			COALESCE(tsii.custom_sales_person,
                (
                    SELECT tst.sales_person
                    FROM `tabSales Team` tst
                    WHERE tst.parent = tsi.name
                    AND tst.parenttype = 'Sales Invoice'
                    ORDER BY tst.idx ASC
                    LIMIT 1
                )
            ) AS sales_person,
			tsii.warehouse,
			tsii.stock_qty,
			tsii.amount
		FROM `tabSales Invoice` tsi
		INNER JOIN  `tabSales Invoice Item` tsii ON tsii.parent = tsi.name
		WHERE
			tsi.docstatus = 1
			{conditions}
		ORDER BY sales_person, tsi.name DESC
		""",
		tuple(values),
		as_dict=1,
	)

	return entries


def get_conditions(filters, date_field):
	conditions = [""]
	values = []

	for field in ["company", "customer", "pos_profile"]:
		if filters.get(field):
			conditions.append(f"tsi.{field}=%s")
			values.append(filters[field])

	if filters.get("sales_person"):
		lft, rgt = frappe.get_value("Sales Person", filters.get("sales_person"), ["lft", "rgt"])
		conditions.append(
			f"exists(select name from `tabSales Person` where lft >= {lft} and rgt <= {rgt} and name=tst.sales_person)"
		)

	if filters.get("from_date"):
		conditions.append(f"tsi.{date_field}>=%s")
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append(f"tsi.{date_field}<=%s")
		values.append(filters["to_date"])

	items = get_items(filters)
	if items:
		conditions.append("tsii.item_code in (%s)" % ", ".join(["%s"] * len(items)))
		values += items
	else:
		# no items found, return nothing
		conditions.append("tsii.item_code = Null")

	return " and ".join(conditions), values


def get_items(filters):
	item = qb.DocType("Item")
	item_query_conditions = []

	if filters.get("item_group"):
		item_group = qb.DocType("Item Group")
		lft, rgt = frappe.db.get_all(
			"Item Group",
			filters={"name": filters.get("item_group")},
			fields=["lft", "rgt"],
			as_list=True,
		)[0]
		item_group_query = (
			qb.from_(item_group)
			.select(item_group.name)
			.where((item_group.lft >= lft) & (item_group.rgt <= rgt))
		)
		item_query_conditions.append(item.item_group.isin(item_group_query))

	items = qb.from_(item).select(item.name).where(Criterion.all(item_query_conditions)).run()
	return items


def get_item_details():
	item_details = {}

	# basic item info
	for d in frappe.db.sql(
		"""SELECT name, item_name, item_group, custom_description_code AS description_code 
		FROM `tabItem`""",
		as_dict=1,
	):
		item_details.setdefault(d.name, d)

	# article attribute
	article_data = frappe.db.sql(
		"""SELECT parent, attribute_value 
		FROM `tabItem Variant Attribute` 
		WHERE attribute = 'Article'""",
		as_dict=1,
	)

	for attr in article_data:
		if attr.parent in item_details:
			item_details[attr.parent]["article"] = attr.attribute_value

	return item_details