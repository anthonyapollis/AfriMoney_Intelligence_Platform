{{
  config(
    materialized      = 'incremental',
    unique_key        = 'transfer_id',
    incremental_strategy = 'merge',
    merge_exclude_columns = ['dbt_inserted_at'],
    on_schema_change  = 'append_new_columns',
    tags              = ['silver', 'intermediate', 'revenue'],
    cluster_by        = ['created_month', 'business_key', 'corridor_code'],
    snowflake_warehouse = 'AFRIMONEY_TRANSFORM_WH'
  )
}}

/*
  int_transfer_profitability
  Enriches each completed transfer with partner cost allocation,
  FX margin breakdown, and profitability classification.
  Grain: one completed transfer (excludes failed/cancelled).

  ── Incremental design ───────────────────────────────────────────────────────
  Full-refreshing 5M+ transfers on every run costs roughly 12 minutes on a
  MEDIUM warehouse and rebuilds history that cannot change. Instead:

    strategy = merge      A transfer is mutable after creation — a payout can
                          settle days later and rewrite completion_minutes,
                          partner_cost_zar and net_revenue_zar. append-only
                          would duplicate those rows; delete+insert would
                          rewrite whole partitions. merge updates in place on
                          transfer_id.

    lookback window       We re-scan `incremental_lookback_days` (default 7)
                          behind the current watermark rather than filtering on
                          strictly-greater-than. Without this, a transfer that
                          settles on day 3 after creation is loaded once with
                          incomplete cost data and never corrected.

    merge_exclude_columns dbt_inserted_at records first-seen time and must
                          survive later merges, so it is excluded from the
                          UPDATE clause.

  Run `dbt run --full-refresh -s int_transfer_profitability` after changing any
  profitability tier boundary, since those reclassify history.
*/

with transfers as (

    select * from {{ ref('stg_transfers') }}
    where is_completed = true

),

{#
    Restrict the scan window. In prod this is the incremental watermark; in dev
    it is additionally clamped to a few recent months so a developer building the
    whole DAG doesn't spend 12 minutes and a few dollars of credit to test a
    one-line change.
#}
transfers_scoped as (

    select * from transfers
    {% if is_incremental() %}
    where created_at >= (
        select coalesce(
            dateadd(day, -{{ var('incremental_lookback_days', 7) }}, max(created_at)),
            '1900-01-01'::timestamp_ntz
        )
        from {{ this }}
    )
    {% elif target.name != 'prod' %}
    where created_at >= dateadd(month, -{{ var('dev_lookback_months', 3) }}, current_date())
    {% endif %}

),

fx as (

    select
        corridor_code,
        date_trunc('day', rate_datetime)::date as rate_date,
        avg(market_rate)    as avg_market_rate,
        avg(customer_rate)  as avg_customer_rate,
        avg(fx_spread_pct)  as avg_spread_pct
    from {{ source('bronze', 'fact_fx_rate') }}
    {% if is_incremental() %}
    where rate_datetime >= (
        select coalesce(
            dateadd(day, -{{ var('incremental_lookback_days', 7) }} - 1, max(created_at)),
            '1900-01-01'::timestamp_ntz
        )
        from {{ this }}
    )
    {% endif %}
    group by 1, 2

),

corridors as (

    select * from {{ ref('corridor_reference') }}

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

        -- Corridor reference attributes (from seed)
        c.corridor_tier,
        c.region,
        c.regulatory_regime,
        c.settlement_partner_type,
        c.is_sadc,

        -- Core amounts
        {{ zar('t.send_amount_zar') }}     as send_amount_zar,
        t.receive_amount,
        {{ zar('t.transfer_fee_zar') }}    as transfer_fee_zar,
        {{ zar('t.vat_zar') }}             as vat_zar,
        {{ zar('t.fx_margin_zar') }}       as fx_margin_zar,
        {{ zar('t.partner_cost_zar') }}    as partner_cost_zar,
        {{ zar('t.gross_revenue_zar') }}   as gross_revenue_zar,
        {{ zar('t.net_revenue_zar') }}     as net_revenue_zar,

        -- FX enrichment
        t.market_fx_rate,
        t.customer_fx_rate,
        t.fx_spread_pct,
        f.avg_market_rate   as daily_avg_market_rate,
        f.avg_spread_pct    as daily_avg_spread_pct,

        -- Profitability ratios
        {{ safe_pct('t.net_revenue_zar',   't.send_amount_zar') }}    as net_margin_pct,
        {{ safe_pct('t.fx_margin_zar',     't.gross_revenue_zar') }}  as fx_revenue_share_pct,
        {{ safe_pct('t.transfer_fee_zar',  't.gross_revenue_zar') }}  as fee_revenue_share_pct,
        {{ safe_pct('t.partner_cost_zar',  't.gross_revenue_zar') }}  as partner_cost_share_pct,

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
        end                                                    as speed_tier,

        t.completion_minutes,

        -- Audit columns. dbt_inserted_at is excluded from merge updates so it
        -- keeps recording when the row was FIRST seen, while dbt_updated_at
        -- moves every time the row is revised by a late settlement.
        current_timestamp()::timestamp_ntz                     as dbt_inserted_at,
        current_timestamp()::timestamp_ntz                     as dbt_updated_at

    from transfers_scoped t
    left join fx f
        on  t.corridor_code   = f.corridor_code
        and t.created_at::date = f.rate_date
    left join corridors c
        on  t.corridor_code = c.corridor_code

)

select * from enriched
