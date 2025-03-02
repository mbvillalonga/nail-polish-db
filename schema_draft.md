# nail-polish-db Schema draft

## Abbreviations

- FK: foreign key

## Tables

### `brands` (class: `Brand`)

- brand_id
- name
- type
- website_url

### `polishes` (class: `Polish`)

- polish_id
- name
- brand_id (FK)
- polish_type
- color_family
- full_desc
- tags
- swatch_photos (FK)
- mani_photos (FK)
- recd_date
- destash_flag

### `swatch_photos` (class: `SwatchPhoto`)

### `mani_photos` (class: `ManiPhoto`)

### `order_logs` (class: `OrderLog`)

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

### `mani_logs` (class: `ManiLog`)

- mani_idx
- mani_date
- polishes_used
- tags
- mani_photos

### `ingredients` (class: `Ingredient`)

- product_name
- ingredient_type
- vendor
- qty_vol
- qty_weight
- particle_size
- order_date (FK)
- recipes (FK)

### `recipes` (class: `Recipe`)

- polish_name
- ingredients
- qtys
- notes

## Relationships

### One-to-one relationships

1. `recipes` to `polishes` DONE

### One-to-many relationships

1. `brands` (one) to `polishes` (many) DONE
2. `polishes` (one) to `swatch_photos` (many) DONE
3. `mani_logs` (one) to `mani_photos` (many) DONE

### Many-to-many relationships

1. `polishes` to `order_logs` DONE
2. `polishes` to `mani_photos` DONE
3. `polishes` to `mani_logs` DONE
4. `ingredients` to `order_logs` DONE
5. `ingredients` to `recipes` DONE
