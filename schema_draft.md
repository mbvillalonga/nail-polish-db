## nail-polish-db Schema draft

### polishes

- polish_idx
- brand_idx (FK)
- type
- color_group
- tags
- swatch_photo
- full_desc
- mani_photos (FK)
- usage_amt
- recd_date
- destash_flag

### brands

- brand_idx
- type
- website_url
- num_owned
- num_destashed

### order-log

- order_date
- order_idx
- order_total
- polishes_bought (FK)
- ingredients_bought (FK)
- num_polishes
- subtotal_polish
- subtotal_ingredient
- subtotal_other
- subtotal_ship_tax
- subtotal_discount
- total_spent
- cost_per_polish

### mani-log

- mani_idx
- mani_date
- polishes_used
- tags
- mani_photos

### ingredient-library

- product_name
- ingredient_type
- vendor
- qty_vol
- qty_weight
- particle_size
- order_date (FK)
- recipes (FK)

### custom-polish-recipes

- polish_name 
- ingredients
- qtys
- notes