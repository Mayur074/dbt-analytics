-- models/staging/stg_customers.sql
-- Staging layer: clean and standardize raw customers data

with source as (
    select * from {{ source('raw', 'raw_customers') }}
),

cleaned as (
    select
        customer_id::varchar                            as customer_id,
        upper(left(trim(first_name), 1)) || lower(substr(trim(first_name), 2)) as first_name,
        upper(left(trim(last_name), 1)) || lower(substr(trim(last_name), 2)) as last_name,
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
