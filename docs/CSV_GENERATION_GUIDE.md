# CSV Generation from Customer Orders Guide

This feature allows you to generate CSV files from customer orders using the catalog.json file as the source of truth. The system maps item codes or item names from customer orders to the catalog and generates a properly formatted CSV file.

## Features

- **Catalog-Based Mapping**: Automatically maps item codes and item names to the catalog
- **Flexible Input**: Accept orders by item code or item name
- **Error Handling**: Reports items that cannot be found in the catalog
- **Multiple Interfaces**: CLI command, API endpoint, and Python utility
- **Catalog Statistics**: View catalog information and item counts

## Quick Start

### 1. Using the Management Command (CLI)

The simplest way to generate a CSV is using the Django management command.

#### From a File

Create a text file with your order (one item per line):

```text
# sample_order.txt
# Format: item_code: quantity OR item_name, quantity

10026, 5
10100: 3
SESAME SEED BLACK PP: 10
VEGETABLE OIL 32.5L, 1
```

Generate the CSV:

```bash
cd backend
python manage.py generate_order_csv --input ../sample_order.txt --output order.csv
```

With category column:

```bash
python manage.py generate_order_csv --input ../sample_order.txt --output order.csv --include-category
```

#### Interactive Mode

Enter items interactively:

```bash
python manage.py generate_order_csv --interactive --output order.csv
```

#### View Catalog Statistics

```bash
python manage.py generate_order_csv --stats
```

### 2. Using the API Endpoint

#### Generate CSV from Text

**Endpoint**: `POST /api/orders/catalog/generate-csv/`

**Headers**:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Request Body**:
```json
{
  "order_text": "10026, 5\n10100: 3\nSESAME SEED BLACK PP: 10",
  "include_category": false
}
```

**Response**: CSV file download

**Example using curl**:
```bash
curl -X POST http://localhost:8000/api/orders/catalog/generate-csv/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_text": "10026, 5\n10100: 3\nSESAME SEED BLACK PP: 10",
    "include_category": false
  }' \
  --output order.csv
```

#### Get Catalog Statistics

**Endpoint**: `GET /api/orders/catalog/stats/`

**Headers**:
- `Authorization: Bearer <token>`

**Response**:
```json
{
  "total_items": 3741,
  "categories": ["Branded", "Nonfood", "Grain Market", ...],
  "category_counts": {
    "Branded": 1291,
    "Nonfood": 1126,
    ...
  },
  "metadata": {
    "version": "1.0",
    "generated_at": "2025-08-12T21:54:12.208469"
  }
}
```

### 3. Using Python Utility

```python
from orders.catalog_mapper import CatalogMapper

# Initialize mapper
mapper = CatalogMapper()

# Define order items
order_items = [
    {'identifier': '10026', 'quantity': 5},
    {'identifier': 'SESAME SEED BLACK PP', 'quantity': 10}
]

# Generate CSV
csv_content, errors = mapper.generate_csv_from_order(order_items, include_category=True)

if errors:
    print("Errors:", errors)

# Save to file
with open('order.csv', 'w') as f:
    f.write(csv_content)
```

## Order Input Format

The system accepts two formats for specifying items:

### Format 1: Colon-separated
```
item_code: quantity
item_name: quantity
```

### Format 2: Comma-separated
```
item_code, quantity
item_name, quantity
```

### Examples

```text
# By item code
10026: 5
10100, 3
18910: 2

# By item name
SESAME SEED BLACK PP: 10
VEGETABLE OIL 32.5L, 1
COW GHEE 12X8OZ: 6

# Comments are supported (lines starting with #)
# Mixed formats work too
```

## Output CSV Format

### Standard Format (3 columns)
```csv
Item Code,Description,Quantity
10026,BLACK CARDAMOM 55LB,5.0
10100,CORIANDER POWDER 50/55LB,3.0
```

### With Category (4 columns)
```csv
Item Code,Description,Quantity,Category
10026,BLACK CARDAMOM 55LB,5.0,Bulk
10100,CORIANDER POWDER 50/55LB,3.0,Bulk
```

## Command Reference

### Management Command Options

```bash
python manage.py generate_order_csv [OPTIONS]
```

**Options**:
- `--input`, `-i`: Input file with order items
- `--output`, `-o`: Output CSV file path (default: order_output.csv)
- `--catalog`, `-c`: Custom path to catalog.json file
- `--include-category`: Include category column in CSV
- `--interactive`: Enter items interactively
- `--stats`: Show catalog statistics

## Error Handling

The system provides clear error messages for common issues:

1. **Item Not Found**: "Item 'XYZ' not found in catalog"
2. **Invalid Quantity**: "Invalid quantity for 'ABC'"
3. **Missing Identifier**: "Missing item identifier"
4. **Empty Order**: "No valid order items found"

Errors are reported without stopping the entire process, so valid items are still processed.

## Integration with Django Models

The system also works with Django Order models:

```python
from orders.models import Order
from orders.utils import CSVGenerator

# Generate CSV for an existing order
order = Order.objects.get(order_number='DD20241114001')
csv_content = CSVGenerator.generate_order_csv(order)
```

## Catalog Information

The catalog contains **3,741 items** across **8 categories**:
- Branded: 1,291 items
- Nonfood: 1,126 items
- Grain Market: 881 items
- Organic: 175 items
- Bulk: 162 items
- Frozen: 80 items
- Mainpage: 16 items
- Supplies: 10 items

## Best Practices

1. **Use Item Codes When Available**: Item codes are unique and provide faster, more accurate matching
2. **Check Errors**: Always review error messages for items that couldn't be mapped
3. **Validate Quantities**: Ensure quantities are positive numbers
4. **Test with Small Orders**: Test the process with a few items before processing large orders
5. **Keep Catalog Updated**: The catalog.json file should be kept up to date with your inventory

## Troubleshooting

### Problem: "Catalog file not found"
**Solution**: Ensure the catalog.json file exists at `docs/catalog/catalog.json` or specify a custom path with `--catalog`

### Problem: "Item not found in catalog"
**Solution**: 
- Check the item code/name spelling
- Use `--stats` to see available categories
- Verify the item exists in the catalog

### Problem: "No valid order items found"
**Solution**: Check your input format. Each line should be: `item: quantity` or `item, quantity`

## API Integration Example

Here's a complete example using JavaScript/fetch:

```javascript
async function generateOrderCSV(orderText) {
  const response = await fetch('/api/orders/catalog/generate-csv/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      order_text: orderText,
      include_category: true
    })
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'order.csv';
    a.click();
  } else {
    const error = await response.json();
    console.error('Error:', error);
  }
}
```

## Support

For issues or questions, please refer to the main project documentation or contact the development team.
