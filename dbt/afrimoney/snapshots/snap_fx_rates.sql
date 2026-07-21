{% snapshot snap_fx_rates %}

{{
  config(
    target_schema  = 'SNAPSHOTS',
    unique_key     = 'corridor_code',
    strategy       = 'check',
    check_cols     = [
      'market_rate',
      'customer_rate',
      'fx_spread_pct',
      'margin_per_unit',
      'is_active'
    ],
    invalidate_hard_deletes = true,
    tags = ['snapshot', 'fx', 'scd2']
  )
}}

/*
  snap_fx_rates — SCD Type 2 via dbt snapshot
  -----------------------------------------------
  Source : BRONZE.FACT_FX_RATE (active rate per corridor)
  Tracks : Market rate moves, customer rate changes, spread compression
           or widening, margin changes, corridor activation/deactivation.

  One row per corridor_code at any point in time.
  dbt_valid_from / dbt_valid_to mark each rate period.
  Use for: FX margin trend analysis, regulatory audits, pricing history.
*/

select
    corridor_code,
    send_currency,
    receive_currency,
    rate_source,

    -- Mutable rate fields (check_cols above)
    market_rate,
    customer_rate,
    fx_spread_pct,
    margin_per_unit,
    is_active,

    -- Most recent rate timestamp for this corridor
    rate_datetime,

    -- Metadata
    _loaded_at

from {{ source('bronze', 'fact_fx_rate') }}
where is_active = true
qualify row_number() over (
    partition by corridor_code
    order by rate_datetime desc
) = 1

{% endsnapshot %}
