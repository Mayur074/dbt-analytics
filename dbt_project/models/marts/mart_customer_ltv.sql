-- models/marts/mart_customer_ltv.sql
-- Business mart: customer lifetime value, RFM segmentation, cohort metrics
-- Materialized as TABLE for fast BI queries

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

customer_metrics as (
    select
        customer_id,
        first_name,
        last_name,
        email,
        country,
        customer_segment,
        signup_date,

        -- LTV metrics
        count(order_id)                                             as total_orders,
        count(case when is_completed then 1 end)                    as completed_orders,
        sum(order_amount)                                           as total_revenue,
        round(avg(order_amount), 2)                                 as avg_order_value,
        round(sum(case when is_completed then order_amount end), 2) as completed_revenue,

        -- RFM inputs
        max(order_date)                                             as last_order_date,
        min(order_date)                                             as first_order_date,
        date_diff('day', min(order_date), max(order_date))          as customer_lifespan_days,

        -- Channel preference
        mode() within group (order by sales_channel)                as preferred_channel

    from customer_orders
    group by 1,2,3,4,5,6,7
),

rfm_scored as (
    select
        *,

        -- Recency score (days since last order — lower = better)
        date_diff('day', last_order_date, current_date)             as recency_days,

        -- Frequency tier
        case
            when total_orders >= 10 then 'HIGH'
            when total_orders >= 5  then 'MEDIUM'
            else 'LOW'
        end                                                         as frequency_tier,

        -- Monetary tier
        case
            when total_revenue >= 1000 then 'HIGH_VALUE'
            when total_revenue >= 300  then 'MID_VALUE'
            else 'LOW_VALUE'
        end                                                         as monetary_tier,

        -- LTV segment
        case
            when total_revenue >= 1000 and total_orders >= 10 then 'CHAMPION'
            when total_revenue >= 500  and total_orders >= 5  then 'LOYAL'
            when total_orders  = 1                            then 'ONE_TIME'
            else 'AT_RISK'
        end                                                         as ltv_segment,

        round(total_revenue / nullif(customer_lifespan_days, 0) * 365, 2) as annualized_ltv

    from customer_metrics
)

select * from rfm_scored
