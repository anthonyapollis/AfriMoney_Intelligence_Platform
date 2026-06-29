{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'risk'],
    cluster_by    = ['business_key', 'risk_month'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_risk_compliance
  Monthly risk & compliance KPIs for the compliance dashboard.
  Grain: business_key + risk_month
*/

with transfer_risk as (
    select
        business_key,
        to_varchar(date_trunc('month', created_datetime), 'YYYY-MM') as risk_month,
        count(*)                                         as total_transfers,
        sum(is_suspected_fraud::int)                     as fraud_flagged_count,
        div0(sum(is_suspected_fraud::int), count(*)) * 10000 as fraud_rate_bps,
        count(case when transfer_status='COMPLETED' then 1 end) as completed_transfers,
        count(case when transfer_status='FAILED'    then 1 end) as failed_transfers,
        count(case when transfer_status='CANCELLED' then 1 end) as cancelled_transfers,
        div0(count(case when transfer_status='COMPLETED' then 1 end), count(*)) * 100 as success_rate_pct,
        avg(payment_attempts)                            as avg_payment_attempts,
        count(case when payment_attempts >= 3 then 1 end) as high_attempt_transfers,
        sum(send_amount_zar)                             as total_volume_zar,
        sum(case when is_suspected_fraud then send_amount_zar else 0 end) as fraud_volume_zar
    from {{ source('bronze', 'fact_remittance_transfer') }}
    group by 1, 2
),

kyc_metrics as (
    select
        business_key,
        count(*)                                                    as total_customers,
        count(case when kyc_level = 'LEVEL_0' then 1 end)          as kyc_level_0,
        count(case when kyc_level = 'LEVEL_1' then 1 end)          as kyc_level_1,
        count(case when kyc_level in ('LEVEL_2','LEVEL_3') then 1 end) as kyc_fully_verified,
        count(case when customer_status = 'SUSPENDED' then 1 end)  as suspended_customers,
        count(case when risk_band in ('HIGH','VERY_HIGH') then 1 end) as high_risk_customers,
        div0(
            count(case when kyc_level in ('LEVEL_2','LEVEL_3') then 1 end),
            count(*)
        ) * 100 as kyc_completion_rate
    from {{ source('bronze', 'dim_customer') }}
    where is_current = true
    group by 1
)

select
    t.business_key,
    t.risk_month,
    t.total_transfers,
    t.fraud_flagged_count,
    t.fraud_rate_bps,
    t.completed_transfers,
    t.failed_transfers,
    t.cancelled_transfers,
    t.success_rate_pct,
    t.avg_payment_attempts,
    t.high_attempt_transfers,
    t.total_volume_zar,
    t.fraud_volume_zar,
    div0(t.fraud_volume_zar, t.total_volume_zar) * 10000 as fraud_volume_bps,
    k.total_customers,
    k.kyc_level_0,
    k.kyc_level_1,
    k.kyc_fully_verified,
    k.kyc_completion_rate,
    k.suspended_customers,
    k.high_risk_customers,
    case
        when t.fraud_rate_bps < 5   then 'green'
        when t.fraud_rate_bps < 10  then 'amber'
        else                             'red'
    end as fraud_rag_status,
    case
        when k.kyc_completion_rate >= 90 then 'green'
        when k.kyc_completion_rate >= 80 then 'amber'
        else                                  'red'
    end as kyc_rag_status,
    current_timestamp() as _dbt_updated_at
from transfer_risk t
left join kyc_metrics k on t.business_key = k.business_key
