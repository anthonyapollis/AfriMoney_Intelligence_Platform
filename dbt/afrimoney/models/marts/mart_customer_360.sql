{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'customer'],
    cluster_by    = ['business_key', 'customer_segment'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_customer_360
  One row per current customer with full behavioural + ML scores.
  Grain: customer_id (IS_CURRENT = TRUE only)
*/

with customers as (
    select * from {{ ref('stg_customers') }}
    where is_current = true
),

transfer_stats as (
    select * from {{ ref('int_customer_transfer_stats') }}
),

-- Wallet balances (latest per customer)
wallet_latest as (
    select
        customer_id,
        max_by(running_balance_zar, entry_datetime) as latest_wallet_balance_zar,
        sum(case when entry_direction='debit'  then amount_zar else 0 end) as total_wallet_cash_in_zar,
        sum(case when entry_direction='credit' then amount_zar else 0 end) as total_wallet_cash_out_zar,
        count(*)                                                            as wallet_entry_count
    from {{ source('bronze', 'fact_wallet_ledger') }}
    group by 1
),

-- Card spending summary
card_stats as (
    select
        customer_id,
        count(*)                                                              as total_card_txns,
        sum(case when transaction_status='APPROVED' then amount_zar else 0 end) as total_card_spend_zar,
        avg(case when transaction_status='APPROVED' then amount_zar else null end) as avg_card_txn_zar,
        count(case when transaction_status='DECLINED' then 1 end)             as card_declines,
        sum(is_fraud_flagged::int)                                            as card_fraud_flags,
        max(transaction_datetime)                                             as last_card_txn_at
    from {{ source('bronze', 'fact_card_transaction') }}
    group by 1
),

-- USD savings (Mama Money)
usd_stats as (
    select
        customer_id,
        current_balance_zar as usd_savings_balance_zar,
        account_status      as usd_account_status
    from {{ source('bronze', 'fact_usd_savings') }}
),

-- Mukuru loan summary
loan_stats as (
    select
        customer_id,
        count(*)                                                              as loan_applications,
        sum(case when decision='APPROVED' then 1 else 0 end)                 as loans_approved,
        sum(case when loan_status in ('DEFAULTED','WRITTEN_OFF') then 1 else 0 end) as loans_defaulted,
        sum(case when decision='APPROVED' then principal_zar else 0 end)     as total_loan_principal_zar,
        avg(probability_of_default)                                           as avg_pd_score,
        max(days_past_due)                                                    as max_dpd
    from {{ source('bronze', 'fact_loan_application') }}
    group by 1
),

assembled as (
    select
        c.customer_sk,
        c.customer_id,
        c.business_key,
        c.age_years,
        c.gender,
        c.nationality,
        c.preferred_language,
        c.registered_at,
        c.registration_month,
        c.registration_channel,
        c.kyc_level,
        c.is_fully_verified,
        c.customer_status,
        c.risk_band,
        c.customer_segment,
        c.monthly_income_band,
        c.employer_type,
        c.has_sa_id,
        c.has_passport,
        c.is_marketing_opt_in,
        c.acquisition_source,
        c.days_since_registration,
        c.is_active,

        -- Transfer behaviour
        coalesce(t.total_transfers,       0)   as total_transfers,
        coalesce(t.completed_transfers,   0)   as completed_transfers,
        coalesce(t.failed_transfers,      0)   as failed_transfers,
        coalesce(t.total_send_zar,        0)   as total_send_zar,
        coalesce(t.avg_send_zar,          0)   as avg_send_zar,
        coalesce(t.total_revenue_generated_zar, 0) as lifetime_revenue_zar,
        coalesce(t.total_fees_paid_zar,   0)   as lifetime_fees_zar,
        t.first_transfer_at,
        t.last_transfer_at,
        coalesce(t.days_since_last_transfer, 999) as days_since_last_transfer,
        coalesce(t.completion_rate,       0)   as transfer_completion_rate,
        coalesce(t.monthly_transfer_rate, 0)   as monthly_transfer_rate,
        coalesce(t.distinct_corridors,    0)   as distinct_corridors,
        coalesce(t.distinct_channels,     0)   as distinct_channels,
        t.preferred_channel,
        t.preferred_payout_method,
        coalesce(t.is_churned, true)           as is_churned,
        coalesce(t.is_high_value, false)       as is_high_value,

        -- Wallet
        coalesce(w.latest_wallet_balance_zar, 0) as wallet_balance_zar,
        coalesce(w.total_wallet_cash_in_zar,  0) as total_wallet_cash_in_zar,
        coalesce(w.wallet_entry_count,         0) as wallet_transactions,

        -- Card
        coalesce(cs.total_card_spend_zar,  0)  as total_card_spend_zar,
        coalesce(cs.total_card_txns,       0)  as total_card_transactions,
        coalesce(cs.avg_card_txn_zar,      0)  as avg_card_txn_zar,
        coalesce(cs.card_declines,         0)  as card_decline_count,
        coalesce(cs.card_fraud_flags,      0)  as card_fraud_flags,
        cs.last_card_txn_at,

        -- USD Savings (Mama Money)
        coalesce(u.usd_savings_balance_zar, 0) as usd_savings_balance_zar,
        u.usd_account_status,

        -- Loans (Mukuru)
        coalesce(l.loan_applications,      0)  as loan_applications,
        coalesce(l.loans_approved,         0)  as loans_approved,
        coalesce(l.loans_defaulted,        0)  as loans_defaulted,
        coalesce(l.total_loan_principal_zar, 0) as total_loan_principal_zar,
        l.avg_pd_score,
        coalesce(l.max_dpd,                0)  as max_days_past_due,

        -- LTV Score (weighted composite)
        round(
            coalesce(t.total_revenue_generated_zar, 0) * 0.60 +
            coalesce(cs.total_card_spend_zar, 0) * 0.002 +
            coalesce(t.completed_transfers, 0) * 5.0 +
            coalesce(w.latest_wallet_balance_zar, 0) * 0.01 +
            coalesce(u.usd_savings_balance_zar, 0) * 0.005
        , 2)                                    as ltv_score,

        current_timestamp()                     as _dbt_updated_at

    from customers c
    left join transfer_stats t  on c.customer_id = t.customer_id
    left join wallet_latest  w  on c.customer_id = w.customer_id
    left join card_stats     cs on c.customer_id = cs.customer_id
    left join usd_stats      u  on c.customer_id = u.customer_id
    left join loan_stats     l  on c.customer_id = l.customer_id
)

select
    *,
    case
        when ltv_score >= 2000 then 'champion'
        when ltv_score >= 500  then 'high'
        when ltv_score >= 100  then 'medium'
        when ltv_score >  0    then 'low'
        else                        'zero'
    end as ltv_band,

    -- Engagement score (0-100)
    least(100, round(
        (1 - least(days_since_last_transfer, 180) / 180.0) * 40 +
        least(monthly_transfer_rate, 5) / 5.0 * 30 +
        (is_fully_verified::int) * 20 +
        (wallet_transactions > 0)::int * 10
    )) as engagement_score

from assembled
