-- models/marts/mart_revenue_analytics.sql
-- Business mart: monthly revenue trends, channel performance, cohort analysis

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

monthly_revenue as (
    select
        order_year,
        order_quarter,
        order_month,
        sales_channel,
        country,
        customer_segment,

        count(order_id)                                 as total_orders,
        count(distinct customer_id)                     as unique_customers,
        sum(order_amount)                               as gross_revenue,
        sum(case when is_completed
            then order_amount end)                      as completed_revenue,
        round(avg(order_amount), 2)                     as avg_order_value,
        count(case when is_completed then 1 end)        as completed_orders,

        round(
            count(case when is_completed then 1 end)::decimal
            / nullif(count(order_id), 0) * 100, 2
        )                                               as completion_rate_pct

    from customer_orders
    group by 1,2,3,4,5,6
),

with_growth as (
    select
        *,
        lag(gross_revenue) over (
            partition by sales_channel, country
            order by order_year, order_month
        )                                               as prev_month_revenue,

        round(
            (gross_revenue - lag(gross_revenue) over (
                partition by sales_channel, country
                order by order_year, order_month
            )) / nullif(lag(gross_revenue) over (
                partition by sales_channel, country
                order by order_year, order_month
            ), 0) * 100, 2
        )                                               as mom_growth_pct

    from monthly_revenue
)

select * from with_growth
order by order_year, order_month, sales_channel
