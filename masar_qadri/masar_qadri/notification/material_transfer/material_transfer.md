<p>The Material Transfer to {{ doc.custom_target_location }} has been initiated. Details are as follows:</p>

<p><b>Document No.:</b> {{ doc.name }} <br />
<b>Source:</b> {{ doc.from_warehouse }} <br />
<b>Target:</b> {{ doc.to_warehouse }} <br />
<b>Date and Time:</b> {{ doc.posting_date }} {{ doc.posting_time }} </p>

<p>{% set total_qty = namespace(value=0) %}
{% for row in doc.items %}
    {% set total_qty.value = total_qty.value + row.qty %}
{% endfor %}</p>

<p><b>Total Quantity:</b> {{ total_qty.value }} </p>

<p><b>Transfer Summary:</b></p>

<table border="1" cellpadding="4" cellspacing="0">
<tr>
    <th>Barcode</th>
    <th>Item</th>
    <th>Remarks</th>
</tr>
{% for item in doc.items %}
<tr>
    <td>{{ item.barcode or "-" }}</td>
    <td>{{ item.item_code }}</td>
    <td>{{ item.custom_remarks or "-" }}</td>
</tr>
{% endfor %}
</table>
