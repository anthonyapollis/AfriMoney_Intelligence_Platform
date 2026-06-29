{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'remittance'],
    cluster_by    = ['business_key', 'created_month'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_remittance
  Monthly corridor-level remittance KPIs for Power BI.
  Grain: business_key + corridor_code + created_month + channel + payment_method
*/

with profitability as (
    select * from {{ ref('int_transfer_profitability') }}
),

transfers as (
    select * from {{ ref('stg_transfers') }}
),

-- All transfers (including non-completed) for funnel metrics
all_transfers_monthly as (
    select
        business_key,
        corridor_code,
        created_month,
        channel,
        payment_method,
        payout_method,
        count(*)                                    as initiated_count,
        sum(is_completed::int)                      as completed_count,
        sum(is_failed::int)                         as failed_count,
        sum(is_cancelled::int)                      as cancelled_count,
        sum(is_refunded::int)                       as refunded_count,
        sum(is_suspected_fraud::int)                as fraud_flagged_count,
        count(distinct sender_customer_id)          as unique_senders,
        count(distinct recipient_id)                as unique_recipients,
        sum(is_first_transfer::int)                 as first_transfers,
        sum(is_repeat_customer::int)                as repeat_transfers,
        avg(payment_attempts)                       as avg_payment_attempts,
        avg(payout_attempts)                        as avg_payout_attempts
    from transfers
    group by 1,2,3,4,5,6
),

-- Completed transfers for financial metrics
completed_monthly as (
    select
        business_key,
        corridor_code,
        created_month,
        channel,
        payment_method,
        payout_method,
        sum(send_amount_zar)                        as total_volume_zar,
        sum(transfer_fee_zar)                       as total_fee_zar,
        sum(fx_margin_zar)                          as total_fx_margin_zar,
        sum(partner_cost_zar)                       as total_partner_cost_zar,
        sum(gross_revenue_zar)                      as total_gross_revenue_zar,
        sum(net_revenue_zar)                        as total_net_revenue_zar,
        avg(send_amount_zar)                        as avg_send_amount_zar,
        avg(net_revenue_zar)                        as avg_revenue_per_transfer_zar,
        avg(fx_spread_pct)                          as avg_fx_spread_pct,
        avg(completion_minutes)                     as avg_completion_minutes,
        median(completion_minutes)                  as median_completion_minutes,
        count(distinct profitability_tier)          as profitability_tiers_present
    from profitability
    group by 1,2,3,4,5,6
),

joined as (
    select
        a.business_key,
        a.corridor_code,
        a.created_month,
        a.channel,
        a.payment_method,
        a.payout_method,

        -- Funnel
        a.initiated_count,
        a.completed_count,
        a.failed_count,
        a.cancelled_count,
        a.refunded_count,
        a.fraud_flagged_count,
        a.unique_senders,
        a.unique_recipients,
        a.first_transfers,
        a.repeat_transfers,
        a.avg_payment_attempts,
        a.avg_payout_attempts,

        -- Success rates
        div0(a.completed_count, a.initiated_count) * 100   as success_rate_pct,
        div0(a.failed_count,    a.initiated_count) * 100   as failure_rate_pct,
        div0(a.cancelled_count, a.initiated_count) * 100   as cancellation_rate_pct,
        div0(a.fraud_flagged_count, a.initiated_count) * 10000  as fraud_rate_bps,

        -- Financial (from completed only)
        coalesce(c.total_volume_zar, 0)                    as total_volume_zar,
        coalesce(c.total_fee_zar, 0)                       as total_fee_zar,
        coalesce(c.total_fx_margin_zar, 0)                 as total_fx_margin_zar,
        coalesce(c.total_partner_cost_zar, 0)              as total_partner_cost_zar,
        coalesce(c.total_gross_revenue_zar, 0)             as total_gross_revenue_zar,
        coalesce(c.total_net_revenue_zar, 0)               as total_net_revenue_zar,
        c.avg_send_amount_zar,
        c.avg_revenue_per_transfer_zar,
        c.avg_fx_spread_pct,
        c.avg_completion_minutes,
        c.median_completion_minutes,

        -- Digital adoption
        (a.channel not in ('branch','booth','retail_partner'))::boolean as is_digital_channel,

        current_timestamp() as _dbt_updated_at

    from all_transfers_monthly a
    left join completed_monthly c
        on  a.business_key    = c.business_key
        and a.corridor_code   = c.corridor_code
        and a.created_month   = c.created_month
        and a.channel         = c.channel
        and a.payment_method  = c.payment_method
        and a.payout_method   = c.payout_method
)

select * from joined
