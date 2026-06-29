{{
  config(
    materialized = 'table',
    tags         = ['silver', 'intermediate', 'revenue'],
    cluster_by   = ['business_key', 'corridor_code']
  )
}}

/*
  int_transfer_profitability
  Enriches each completed transfer with partner cost allocation,
  FX margin breakdown, and profitability classification.
  Grain: one completed transfer (excludes failed/cancelled).
*/

with transfers as (
    select * from {{ ref('stg_transfers') }}
    where is_completed = true
),

fx as (
    select
        corridor_code,
        date_trunc('day', rate_datetime)::date as rate_date,
        avg(market_rate)    as avg_market_rate,
        avg(customer_rate)  as avg_customer_rate,
        avg(fx_spread_pct)  as avg_spread_pct
    from {{ source('bronze', 'fact_fx_rate') }}
    group by 1, 2
),

enriched as (
    select
        t.transfer_id,
        t.business_key,
        t.corridor_code,
        t.send_country,
        t.receive_country,
        t.channel,
        t.payment_method,
        t.payout_method,
        t.created_at,
        t.created_month,
        t.created_year,

        -- Core amounts
        t.send_amount_zar,
        t.receive_amount,
        t.transfer_fee_zar,
        t.vat_zar,
        t.fx_margin_zar,
        t.partner_cost_zar,
        t.gross_revenue_zar,
        t.net_revenue_zar,

        -- FX enrichment
        t.market_fx_rate,
        t.customer_fx_rate,
        t.fx_spread_pct,
        f.avg_market_rate   as daily_avg_market_rate,
        f.avg_spread_pct    as daily_avg_spread_pct,

        -- Profitability ratios
        div0(t.net_revenue_zar,  t.send_amount_zar)  * 100  as net_margin_pct,
        div0(t.fx_margin_zar,    t.gross_revenue_zar) * 100  as fx_revenue_share_pct,
        div0(t.transfer_fee_zar, t.gross_revenue_zar) * 100  as fee_revenue_share_pct,
        div0(t.partner_cost_zar, t.gross_revenue_zar) * 100  as partner_cost_share_pct,

        -- Profitability tier
        case
            when t.net_revenue_zar >= 200  then 'platinum'
            when t.net_revenue_zar >= 100  then 'gold'
            when t.net_revenue_zar >= 50   then 'silver'
            when t.net_revenue_zar >= 0    then 'bronze'
            else                                'loss'
        end                                                    as profitability_tier,

        -- Completion speed tier
        case
            when t.completion_minutes <= 15   then 'instant'
            when t.completion_minutes <= 60   then 'fast'
            when t.completion_minutes <= 1440 then 'same_day'
            else                                   'multi_day'
        end                                                    as speed_tier

    from transfers t
    left join fx f
        on t.corridor_code = f.corridor_code
        and t.created_at::date = f.rate_date
)

select * from enriched
