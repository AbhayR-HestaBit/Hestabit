# Product Query Engine

## GET /products

## Supported Query Parameters

- `search` 
  Example: `?search=phone`

- `status` 
  Example: `?status=active`

- `minPrice`, `maxPrice`
  Example: `?minPrice=100&maxPrice=500`

- `tags`
  Example: `?tags=apple,android`

- `sort` 
  Format: `field:asc|desc` 
  Example: `?sort=price:desc`

- `page` 
  Default: `1`

- `limit`
  Default: `10`

- `includeDeleted` 
  Example: `?includeDeleted=true`

## Default Behavior

- Soft deleted products are excluded
- Results sorted by newest first if no sort provided

## Examples

## /products (Get all products:)

## /products?search=phone&minPrice=100&sort=price:asc (Search with filters and sorting:)

## /products?page=2&limit=5 (Paginated result:)

## /products?includeDeleted=true (Include deleted products:)

