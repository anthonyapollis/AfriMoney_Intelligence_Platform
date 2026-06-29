{{
  config(
    materialized = 'view',
    tags         = ['silver', 'staging', 'transfers']
  )
}}

/*
  stg_transfers
  Staging view over BRONZE.FACT_REMITTANCE_TRANSFER.
  Applies:
    - Column renames for consistency
    - Type casts
    - Derived temporal fields
    - Revenue band classifications
  No business logic — that lives in intermediate models.
*/

with source as (
    select * from {{ source('bronze', 'fact_remittance_transfer') }}
),

staged as (
    select
        -- Keys
        transfer_id,
        transfer_reference,
        business_key,
        sender_customer_id,
        recipient_id,
        corridor_code,

        -- Geography
        send_country,
        receive_country,
        send_currency,
        receive_currency,

        -- Channel / method
        channel,
        payment_method,
        payout_method,

        -- Timestamps
        created_datetime::timestamp_ntz                              as created_at,
        completed_datetime::timestamp_ntz                           as completed_at,
        created_date_key,
        completed_date_key,
        transfer_status,

        -- Temporal derived
        date_trunc('month', created_datetime)::date                 as created_month,
        date_part('year',  created_datetime)::int                   as created_year,
        date_part('month', created_datetime)::int                   as created_month_num,
        date_part('dow',   created_datetime)::int                   as created_dow,
        date_part('hour',  created_datetime)::int                   as created_hour,
        (date_part('dow', created_datetime) >= 5)::boolean          as is_weekend,

        -- Monetary
        send_amount_zar,
        receive_amount,
        transfer_fee_zar,
        vat_zar,
        fx_margin_zar,
        partner_cost_zar,
        gross_revenue_zar,
        net_revenue_zar,

        -- FX
        market_fx_rate,
        customer_fx_rate,
        fx_spread_pct,

        -- Operational
        payment_attempts,
        payout_attempts,
        completion_minutes,

        -- Flags
        is_completed,
        is_failed,
        is_cancelled,
        is_refunded,
        is_first_transfer,
        is_repeat_customer,
        is_suspected_fraud,

        -- Derived bands (used in downstream ML features)
        case
            when send_amount_zar < 500   then 'micro'
            when send_amount_zar < 1000  then 'small'
            when send_amount_zar < 2000  then 'medium'
            when send_amount_zar < 5000  then 'large'
            else                              'xlarge'
        end                                                          as send_amount_band,

        case
            when net_revenue_zar < 0    then 'negative'
            when net_revenue_zar < 50   then 'low'
            when net_revenue_zar < 150  then 'medium'
            when net_revenue_zar < 300  then 'high'
            else                             'premium'
        end                                                          as revenue_band,

        -- Log transform for ML (avoids skewness)
        ln(greatest(send_amount_zar, 1))                            as send_amount_log,
        iff(send_amount_zar > 0, transfer_fee_zar / send_amount_zar, null)
                                                                     as fee_pct

    from source
    where created_datetime is not null
)

select * from staged
