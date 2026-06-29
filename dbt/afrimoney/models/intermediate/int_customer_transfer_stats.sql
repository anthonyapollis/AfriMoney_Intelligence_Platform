{{
  config(
    materialized = 'table',
    tags         = ['silver', 'intermediate', 'customer'],
    cluster_by   = ['business_key']
  )
}}

/*
  int_customer_transfer_stats
  Aggregates all transfer behaviour per customer.
  Used by:
    - mart_customer_360
    - Snowpark ML feature store (churn, fraud)
*/

with transfers as (
    select * from {{ ref('stg_transfers') }}
),

customer_stats as (
    select
        sender_customer_id                                              as customer_id,
        business_key,

        -- Volume
        count(*)                                                        as total_transfers,
        sum(is_completed::int)                                          as completed_transfers,
        sum(is_failed::int)                                             as failed_transfers,
        sum(is_cancelled::int)                                          as cancelled_transfers,
        sum(is_suspected_fraud::int)                                    as fraud_flagged_transfers,

        -- Monetary
        sum(case when is_completed then send_amount_zar else 0 end)     as total_send_zar,
        avg(case when is_completed then send_amount_zar else null end)   as avg_send_zar,
        stddev(case when is_completed then send_amount_zar else null end) as stddev_send_zar,
        sum(case when is_completed then net_revenue_zar else 0 end)     as total_revenue_generated_zar,
        sum(case when is_completed then transfer_fee_zar else 0 end)    as total_fees_paid_zar,

        -- Recency / Frequency
        min(created_at)                                                 as first_transfer_at,
        max(created_at)                                                 as last_transfer_at,
        datediff('day', min(created_at), max(created_at))              as active_span_days,
        datediff('day', max(created_at), current_timestamp())          as days_since_last_transfer,

        -- Derived rates
        div0(sum(is_completed::int), count(*))                          as completion_rate,
        div0(sum(is_failed::int), count(*))                             as failure_rate,

        -- Transfer frequency (transfers per 30 days of active span)
        div0(count(*), greatest(datediff('day', min(created_at), current_timestamp()), 1)) * 30
                                                                        as monthly_transfer_rate,

        -- Channel diversity
        count(distinct channel)                                         as distinct_channels,
        count(distinct corridor_code)                                   as distinct_corridors,
        count(distinct receive_country)                                  as distinct_receive_countries,

        -- Preferred channel (mode)
        mode(channel)                                                   as preferred_channel,
        mode(payout_method)                                             as preferred_payout_method,

        -- Churn flag: no transfer in last 90 days
        (datediff('day', max(created_at), current_timestamp()) > {{ var('churn_lookback_days') }})::boolean
                                                                        as is_churned,

        -- High-value flag
        (sum(case when is_completed then send_amount_zar else 0 end) > 50000)::boolean
                                                                        as is_high_value

    from transfers
    group by 1, 2
)

select * from customer_stats
