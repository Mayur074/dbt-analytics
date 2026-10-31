-- models/staging/stg_products.sql
-- Staging layer: clean and standardize raw products data

with source as (
    select * from {{ source('raw', 'raw_products') }}
),

cleaned as (
    select
        product_id::varchar                             as product_id,
        trim(product_name)                              as product_name,
        upper(trim(category))                           as category,
        round(cast(price as decimal(10,2)), 2)          as unit_price,
        coalesce(cast(stock_quantity as integer), 0)    as stock_quantity,
        cast(created_at as timestamp)                   as created_at

    from source
    where
        product_id is not null
        and product_name is not null
        and price > 0
)

select * from cleaned
