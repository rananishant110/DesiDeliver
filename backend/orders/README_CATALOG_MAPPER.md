# Catalog Mapper - CSV Generation from Customer Orders

## Overview

The Catalog Mapper is a utility that generates CSV files from customer orders using the `catalog.json` file as the source of truth. It intelligently maps item codes and item names to catalog entries, providing a seamless way to convert customer orders into structured CSV format.

## Quick Start

### Command Line Usage

```bash
# Generate CSV from a text file
python manage.py generate_order_csv --input order.txt --output result.csv

# Include category column
python manage.py generate_order_csv --input order.txt --output result.csv --include-category

# Interactive mode
python manage.py generate_order_csv --interactive

# View catalog statistics
python manage.py generate_order_csv --stats
```

### Python API Usage

```python
from orders.catalog_mapper import CatalogMapper

# Initialize mapper
mapper = CatalogMapper()

# Define order items
order_items = [
    {'identifier': '10026', 'quantity': 5},
    {'identifier': 'VEGETABLE OIL 32.5L', 'quantity': 2}
]

# Generate CSV
csv_content, errors = mapper.generate_csv_from_order(order_items)

# Handle results
if errors:
    print("Errors:", errors)
    
with open('order.csv', 'w') as f:
    f.write(csv_content)
```

### REST API Usage

```bash
# Generate CSV
curl -X POST http://localhost:8000/api/orders/catalog/generate-csv/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_text": "10026, 5\n10100: 3",
    "include_category": true
  }' \
  --output order.csv

# Get catalog stats
curl -X GET http://localhost:8000/api/orders/catalog/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Module Structure

### `catalog_mapper.py`

Core utility class for catalog operations:

- `CatalogMapper` - Main class
  - `load_catalog()` - Load and index catalog data
  - `find_catalog_item(identifier)` - Find item by code or name
  - `map_order_items(order_items)` - Map order items to catalog
  - `generate_csv_from_order(order_items)` - Generate CSV content
  - `parse_order_from_text(text)` - Parse text orders
  - `get_catalog_stats()` - Get catalog statistics

### Management Command

`management/commands/generate_order_csv.py`

Django management command with options:
- `--input` / `-i` - Input file path
- `--output` / `-o` - Output CSV path
- `--catalog` / `-c` - Custom catalog path
- `--include-category` - Add category column
- `--interactive` - Interactive entry mode
- `--stats` - Show catalog statistics

### API Views

`views.py` additions:
- `generate_order_csv_from_text()` - POST endpoint for CSV generation
- `get_catalog_stats()` - GET endpoint for catalog stats

### URL Routes

`urls.py` additions:
- `/api/orders/catalog/generate-csv/` - CSV generation
- `/api/orders/catalog/stats/` - Catalog statistics

## Input Format

The system accepts two formats:

```text
# Format 1: Colon-separated
item_code: quantity
item_name: quantity

# Format 2: Comma-separated
item_code, quantity
item_name, quantity

# Comments supported (lines starting with #)
# Example:
10026, 5
BLACK CARDAMOM PP: 3
VEGETABLE OIL 32.5L, 2
```

## Output Format

### Standard CSV (3 columns)
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

## Error Handling

The system provides detailed error messages:

```python
errors = [
    "Row 2: Item 'INVALID_ITEM' not found in catalog",
    "Row 3: Invalid quantity for 'ABC'",
    "Row 4: Missing item identifier"
]
```

Errors don't stop processing - valid items are still included in the CSV.

## Testing

Run the test suite:

```bash
python manage.py test orders.tests_catalog_mapper
```

Current test coverage:
- ✅ Catalog loading
- ✅ Item lookup (by code and name)
- ✅ Order mapping (success and error cases)
- ✅ CSV generation
- ✅ Text parsing
- ✅ Statistics
- ✅ Integration tests

## Catalog Information

The catalog contains:
- **Total Items**: 3,741
- **Categories**: 8
  - Branded: 1,291 items
  - Nonfood: 1,126 items
  - Grain Market: 881 items
  - Organic: 175 items
  - Bulk: 162 items
  - Frozen: 80 items
  - Mainpage: 16 items
  - Supplies: 10 items

## Performance

The catalog mapper uses in-memory indexing for fast lookups:
- Catalog loaded once on first use
- O(1) lookup by item code
- O(1) lookup by item name (exact match)
- Case-insensitive name matching supported

## Dependencies

- Python 3.8+
- Django 5.2+
- Standard library: `csv`, `json`, `io`, `pathlib`

## Examples

See `example_usage.py` in the project root for 5 comprehensive examples covering:
1. Basic CSV generation
2. Parsing from text
3. Catalog statistics
4. Error handling
5. Item lookup

## Documentation

Full documentation available at:
- `docs/CSV_GENERATION_GUIDE.md` - Complete user guide
- `example_usage.py` - Working code examples
- `sample_order.txt` - Sample order file

## Support

For issues or questions:
1. Check the documentation
2. Review the test cases
3. Run the example script
4. Contact the development team

## Contributing

When contributing to this module:
1. Add tests for new features
2. Update documentation
3. Follow existing code style
4. Ensure all tests pass

## License

This module is part of the DesiDeliver project.
