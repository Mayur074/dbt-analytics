-- models/staging/stg_orders.sql
-- Staging layer: clean and standardize raw orders data
-- Applies type casting, null handling, and field renaming

with source as (
    select * from {{ ref('raw_orders') }}
),

cleaned as (
    select
        order_id::varchar                           as order_id,
        customer_id::varchar                        as customer_id,
        cast(order_date as date)                    as order_date,
        upper(trim(status))                         as order_status,
        round(cast(amount as decimal(10,2)), 2)     as order_amount,
        coalesce(upper(trim(channel)), 'UNKNOWN')   as sales_channel,
        cast(created_at as timestamp)               as created_at

    from source
    where
        order_id is not null
        and customer_id is not null
        and order_date is not null
        and amount > 0
)

select * from cleaned
