-- models/staging/stg_customers.sql
-- Staging layer: clean and standardize raw customers data

with source as (
    select * from {{ ref('raw_customers') }}
),

cleaned as (
    select
        customer_id::varchar                            as customer_id,
        initcap(trim(first_name))                       as first_name,
        initcap(trim(last_name))                        as last_name,
        lower(trim(email))                              as email,
        upper(trim(country))                            as country,
        coalesce(upper(trim(segment)), 'STANDARD')      as customer_segment,
        cast(signup_date as date)                       as signup_date,
        cast(created_at as timestamp)                   as created_at

    from source
    where
        customer_id is not null
        and email is not null
        and email like '%@%'
)

select * from cleaned
