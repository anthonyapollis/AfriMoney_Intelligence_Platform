{{
  config(
    materialized  = 'dynamic_table',
    snowflake_warehouse = 'AFRIMONEY_STREAM_WH',
    target_lag    = '5 minutes',
    refresh_mode  = 'INCREMENTAL',
    initialize    = 'ON_CREATE',
    on_configuration_change = 'apply',
    tags          = ['gold', 'mart', 'realtime']
  )
}}

/*
  mart_corridor_live
  Near-real-time corridor health, for the ops wallboard.

  -- Why a Dynamic Table rather than an incremental model -------------------
  Every other mart in this project is batch: dbt runs, the table is rebuilt, the
  data is as fresh as the last run. That is correct for finance reporting, where
  a stable daily snapshot is a feature -- numbers that shift under a reviewer
  are worse than numbers that are a few hours old.

  Ops has the opposite requirement. When a settlement partner goes down on the
  ZA-ZW corridor, the wallboard needs to show it within minutes, not at 6am
  tomorrow. Options were:

    scheduled dbt runs every 5 min   Wasteful. The warehouse resumes, scans, and
                                     rebuilds regardless of whether anything
                                     changed, and dbt Cloud job minutes are
                                     billed per invocation.

    Snowflake Stream + Task          Works, but it is imperative plumbing that
                                     lives outside dbt: the DAG no longer
                                     describes the true lineage, and the task
                                     has to be deployed and monitored separately.

    Dynamic Table  <-- chosen        Declarative. We state a target_lag and
                                     Snowflake works out the refresh schedule and
                                     does incremental maintenance automatically.
                                     It stays a dbt node, so it appears in the
                                     DAG, in docs, and in the lineage graph.

  target_lag of 5 minutes is a deliberate cost/latency trade. Below roughly
  1 minute Snowflake tends to fall back to full refreshes on a join this wide,
  which costs materially more for latency nobody on the ops floor can act on.

  refresh_mode INCREMENTAL is set explicitly rather than left to AUTO so that a
  future query change which silently breaks incrementalisation shows up as an
  error at deploy time, not as a surprise on the credit bill.
*/

with recent_transfers as (

    select
        business_key,
        corridor_code,
        created_at,
        transfer_status,
        is_completed,
        is_failed,
        is_suspected_fraud,
        send_amount_zar,
        net_revenue_zar,
        completion_minutes,
        payout_method
    from {{ ref('stg_transfers') }}
    -- Rolling 24h window. Bounded deliberately: an unbounded dynamic table over
    -- 5M rows cannot refresh incrementally on a 5-minute lag.
    where created_at >= dateadd(hour, -24, current_timestamp())

),

corridors as (

    select
        corridor_code,
        receive_country_name,
        corridor_tier,
        region,
        settlement_partner_type
    from {{ ref('corridor_reference') }}

),

live_agg as (

    select
        t.business_key,
        t.corridor_code,
        c.receive_country_name,
        c.corridor_tier,
        c.region,
        c.settlement_partner_type,

        count(*)                                       as transfers_24h,
        sum(t.is_completed::int)                       as completed_24h,
        sum(t.is_failed::int)                          as failed_24h,
        sum(t.is_suspected_fraud::int)                 as fraud_flagged_24h,

        {{ zar('sum(t.send_amount_zar)') }}            as volume_zar_24h,
        {{ zar('sum(t.net_revenue_zar)') }}            as net_revenue_zar_24h,

        {{ safe_pct('sum(t.is_completed::int)', 'count(*)') }}  as success_rate_pct_24h,
        {{ safe_pct('sum(t.is_failed::int)',    'count(*)') }}  as failure_rate_pct_24h,

        avg(t.completion_minutes)                      as avg_completion_minutes_24h,
        median(t.completion_minutes)                   as median_completion_minutes_24h,

        max(t.created_at)                              as last_transfer_at,
        datediff(minute, max(t.created_at), current_timestamp()) as minutes_since_last_transfer

    from recent_transfers t
    left join corridors c
        on t.corridor_code = c.corridor_code
    group by 1,2,3,4,5,6

),

scored as (

    select
        *,

        -- Ops severity. Ordered most-severe first so the wallboard can sort on
        -- it directly without a CASE in the BI layer.
        case
            when transfers_24h = 0                              then 'NO_TRAFFIC'
            when minutes_since_last_transfer > 120               then 'STALLED'
            when success_rate_pct_24h < 80                       then 'CRITICAL'
            when success_rate_pct_24h < 92                       then 'DEGRADED'
            when avg_completion_minutes_24h > 240                then 'SLOW'
            else                                                      'HEALTHY'
        end                                                     as corridor_health_status

    from live_agg

)

select * from scored
