import frappe


@frappe.whitelist()
def get_color_code(name):
    cc_sql = frappe.db.sql("""
                            SELECT DISTINCT 
                                tiav.custom_color 
                            FROM 
                                `tabItem` ti 
                            INNER JOIN 
                                `tabItem Variant Attribute` tiva ON ti.name = tiva.parent 
                            INNER JOIN 
                                `tabItem Attribute` tia ON tiva.`attribute` = tia.attribute_name 
                            INNER JOIN 
                                `tabItem Attribute Value` tiav ON tia.name = tiav.parent
                            WHERE 
                                ti.name = %s 
                                AND tiva.`attribute` = 'Colour' 
                                AND tiva.attribute_value = tiav.attribute_value 
                           """,(name), as_dict=True)
    
    color_code = None    
    if cc_sql and cc_sql[0] and cc_sql[0]['custom_color']:
        color_code = cc_sql[0]['custom_color']
    return color_code

##