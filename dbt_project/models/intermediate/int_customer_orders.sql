-- models/intermediate/int_customer_orders.sql
-- Intermediate layer: join orders with customers, compute order-level metrics

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

joined as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.order_status,
        o.order_amount,
        o.sales_channel,
        c.first_name,
        c.last_name,
        c.email,
        c.country,
        c.customer_segment,
        c.signup_date,

        -- Derived fields
        date_diff('day', c.signup_date, o.order_date)   as days_since_signup,
        date_part('year', o.order_date)::integer         as order_year,
        date_part('month', o.order_date)::integer        as order_month,
        date_part('quarter', o.order_date)::integer      as order_quarter,

        case
            when o.order_status = 'COMPLETED'  then true
            when o.order_status = 'DELIVERED'  then true
            else false
        end                                              as is_completed

    from orders o
    left join customers c using (customer_id)
)

select * from joined
