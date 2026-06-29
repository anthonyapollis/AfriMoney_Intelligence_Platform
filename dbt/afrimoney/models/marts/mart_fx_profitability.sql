{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'fx'],
    cluster_by    = ['business_key', 'corridor_code'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_fx_profitability
  Corridor-level FX margin and profitability analysis.
  Grain: business_key + corridor_code + rate_month
*/

with fx_rates as (
    select
        to_varchar(date_trunc('month', rate_date), 'YYYY-MM') as rate_month,
        source_currency,
        destination_currency,
        corridor_code,
        avg(interbank_rate)      as avg_interbank_rate,
        avg(applied_rate)        as avg_applied_rate,
        avg(spread_pct)          as avg_spread_pct,
        min(spread_pct)          as min_spread_pct,
        max(spread_pct)          as max_spread_pct,
        stddev(spread_pct)       as spread_volatility,
        count(*)                 as rate_data_points
    from {{ source('bronze', 'fact_fx_rate') }}
    group by 1, 2, 3, 4
),

transfer_volumes as (
    select
        business_key,
        corridor_code,
        to_varchar(date_trunc('month', created_datetime), 'YYYY-MM') as rate_month,
        sum(case when transfer_status = 'COMPLETED' then send_amount_zar else 0 end) as total_volume_zar,
        sum(case when transfer_status = 'COMPLETED' then fx_margin_zar  else 0 end) as total_fx_revenue_zar,
        count(case when transfer_status = 'COMPLETED' then 1 end)                   as completed_transfers
    from {{ source('bronze', 'fact_remittance_transfer') }}
    group by 1, 2, 3
),

joined as (
    select
        tv.business_key,
        tv.corridor_code,
        tv.rate_month,
        fx.source_currency,
        fx.destination_currency,
        fx.avg_interbank_rate,
        fx.avg_applied_rate,
        fx.avg_spread_pct,
        fx.min_spread_pct,
        fx.max_spread_pct,
        fx.spread_volatility,
        fx.rate_data_points,
        coalesce(tv.total_volume_zar,      0) as total_volume_zar,
        coalesce(tv.total_fx_revenue_zar,  0) as total_fx_revenue_zar,
        coalesce(tv.completed_transfers,   0) as completed_transfers,
        div0(tv.total_fx_revenue_zar, tv.total_volume_zar) * 100 as effective_margin_pct,
        case
            when fx.avg_spread_pct >= 6   then 'high_margin'
            when fx.avg_spread_pct >= 4   then 'standard'
            when fx.avg_spread_pct >= 2   then 'competitive'
            else                               'thin'
        end as corridor_margin_tier,
        current_timestamp() as _dbt_updated_at
    from transfer_volumes tv
    left join fx_rates fx
        on  tv.corridor_code = fx.corridor_code
        and tv.rate_month    = fx.rate_month
)

select * from joined
