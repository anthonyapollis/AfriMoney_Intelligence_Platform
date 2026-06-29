{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'wallet', 'card'],
    cluster_by    = ['business_key', 'activity_month'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_wallet_card
  Monthly wallet and card product analytics.
  Grain: business_key + activity_month
*/

with wallet_monthly as (
    select
        business_key,
        to_varchar(date_trunc('month', entry_datetime), 'YYYY-MM') as activity_month,
        count(distinct customer_id)  as wallet_active_customers,
        count(*)                     as wallet_entries,
        sum(case when entry_direction='debit'  then amount_zar else 0 end) as total_cash_in_zar,
        sum(case when entry_direction='credit' then amount_zar else 0 end) as total_cash_out_zar,
        avg(running_balance_zar)     as avg_running_balance_zar,
        count(distinct entry_type)   as entry_type_count
    from {{ source('bronze', 'fact_wallet_ledger') }}
    group by 1, 2
),

card_monthly as (
    select
        business_key,
        to_varchar(date_trunc('month', transaction_datetime), 'YYYY-MM') as activity_month,
        count(distinct customer_id)  as card_active_customers,
        count(*)                     as total_card_txns,
        count(case when transaction_status='APPROVED' then 1 end) as approved_txns,
        count(case when transaction_status='DECLINED' then 1 end) as declined_txns,
        sum(case when transaction_status='APPROVED' then amount_zar else 0 end) as total_card_spend_zar,
        avg(case when transaction_status='APPROVED' then amount_zar else null end) as avg_card_spend_zar,
        sum(is_fraud_flagged::int)   as fraud_flagged_txns,
        div0(
            count(case when transaction_status='APPROVED' then 1 end),
            count(*)
        ) * 100 as card_approval_rate
    from {{ source('bronze', 'fact_card_transaction') }}
    group by 1, 2
)

select
    coalesce(w.business_key,      c.business_key)      as business_key,
    coalesce(w.activity_month,    c.activity_month)    as activity_month,
    coalesce(w.wallet_active_customers, 0)             as wallet_active_customers,
    coalesce(w.wallet_entries,          0)             as wallet_entries,
    coalesce(w.total_cash_in_zar,       0)             as wallet_cash_in_zar,
    coalesce(w.total_cash_out_zar,      0)             as wallet_cash_out_zar,
    coalesce(w.avg_running_balance_zar, 0)             as avg_wallet_balance_zar,
    coalesce(c.card_active_customers,   0)             as card_active_customers,
    coalesce(c.total_card_txns,         0)             as total_card_txns,
    coalesce(c.approved_txns,           0)             as approved_txns,
    coalesce(c.declined_txns,           0)             as declined_txns,
    coalesce(c.total_card_spend_zar,    0)             as total_card_spend_zar,
    c.avg_card_spend_zar,
    coalesce(c.fraud_flagged_txns,      0)             as card_fraud_txns,
    coalesce(c.card_approval_rate,      0)             as card_approval_rate_pct,
    current_timestamp() as _dbt_updated_at
from wallet_monthly w
full outer join card_monthly c
    on  w.business_key   = c.business_key
    and w.activity_month = c.activity_month
