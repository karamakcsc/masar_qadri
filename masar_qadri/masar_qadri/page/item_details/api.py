import frappe

@frappe.whitelist()
def get_items_with_filters(item_group=None, article=None, size=None, color=None, season=None, warehouse=None):
    filters = []
    values = {}

    base_query = """
        SELECT DISTINCT i.name, i.item_name, i.item_group, i.brand
        FROM `tabItem` i
        WHERE i.disabled = 0
    """

    if item_group:
        filters.append("i.item_group = %(item_group)s")
        values["item_group"] = item_group

    # Build attribute filters - each attribute must match (AND logic)
    for field, val in {"Article": article, "Size": size, "Color": color, "Season": season}.items():
        if val:
            subquery = f"""
                i.name IN (
                    SELECT iva.parent 
                    FROM `tabItem Variant Attribute` iva 
                    WHERE iva.attribute = %(attr_{field.lower()})s 
                    AND iva.attribute_value = %(val_{field.lower()})s
                )
            """
            filters.append(subquery)
            values[f"attr_{field.lower()}"] = field
            values[f"val_{field.lower()}"] = val

    if filters:
        base_query += " AND " + " AND ".join(filters)

    base_query += " ORDER BY i.item_name LIMIT 200"

    items = frappe.db.sql(base_query, values=values, as_dict=True)

    # Get attributes and stock for each item
    for item in items:
        # Fetch all attributes
        attributes = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": item["name"]},
            fields=["attribute", "attribute_value"]
        )
        
        # Initialize attribute fields
        item["article"] = ""
        item["season"] = ""
        item["color"] = ""
        item["size"] = ""
        item["style"] = ""
        
        # Map attributes to their respective fields
        for attr in attributes:
            attr_name = attr.get("attribute", "").lower()
            attr_value = attr.get("attribute_value", "")
            
            if attr_name == "article":
                item["article"] = attr_value
            elif attr_name == "season":
                item["season"] = attr_value
            elif attr_name == "color":
                item["color"] = attr_value
            elif attr_name == "size":
                item["size"] = attr_value
            elif attr_name == "style":
                item["style"] = attr_value

        # Fetch stock information (exclude Transit warehouses)
        stock_query = """
            SELECT b.warehouse, b.actual_qty
            FROM `tabBin` b
            INNER JOIN `tabWarehouse` w ON b.warehouse = w.name
            WHERE b.item_code = %(item_code)s
            AND (w.warehouse_type IS NULL OR w.warehouse_type != 'Transit')
        """
        
        stock_values = {"item_code": item["name"]}
        
        if warehouse:
            stock_query += " AND b.warehouse = %(warehouse)s"
            stock_values["warehouse"] = warehouse
        
        item["stock"] = frappe.db.sql(stock_query, values=stock_values, as_dict=True)

    return items