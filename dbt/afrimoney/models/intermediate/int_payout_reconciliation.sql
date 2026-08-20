{{
  config(
    materialized = 'table',
    tags         = ['silver', 'intermediate', 'reconciliation'],
    cluster_by   = ['business_key', 'created_month']
  )
}}

/*
  int_payout_reconciliation
  Reconciles each completed transfer's committed send amount against what
  FACT_PAYOUT actually disbursed through the recipient-side partner network.
  Surfaces the "Partner Settlement Variance" KPI already referenced in the
  AfriMoney ebook glossary: what was disbursed vs. what was settled.
  Grain: one row per completed transfer_id.
*/

with completed_transfers as (
    select
        transfer_id,
        business_key,
        corridor_code,
        receive_country,
        created_month,
        send_amount_zar   as committed_amount_zar,
        receive_amount
    from {{ ref('stg_transfers') }}
    where is_completed = true
),

successful_payouts as (
    select
        transfer_id,
        sum(amount_zar_equivalent)   as disbursed_amount_zar,
        sum(amount_receive_currency) as disbursed_amount_receive_currency,
        count(*)                     as successful_payout_count,
        count(distinct partner_code) as settling_partner_count
    from {{ source('bronze', 'fact_payout') }}
    where payout_status = 'SUCCESS'
    group by 1
),

payout_attempts as (
    select
        transfer_id,
        count(*)                                     as total_payout_attempts_recorded,
        sum(iff(payout_status = 'FAILED', 1, 0))      as failed_attempt_count
    from {{ source('bronze', 'fact_payout') }}
    group by 1
),

reconciled as (
    select
        c.transfer_id,
        c.business_key,
        c.corridor_code,
        c.receive_country,
        c.created_month,

        c.committed_amount_zar,
        c.receive_amount,
        coalesce(sp.disbursed_amount_zar, 0)               as disbursed_amount_zar,
        coalesce(sp.disbursed_amount_receive_currency, 0)  as disbursed_amount_receive_currency,
        coalesce(sp.successful_payout_count, 0)            as successful_payout_count,
        coalesce(sp.settling_partner_count, 0)             as settling_partner_count,
        coalesce(pa.total_payout_attempts_recorded, 0)     as total_payout_attempts_recorded,
        coalesce(pa.failed_attempt_count, 0)               as failed_attempt_count,

        round(coalesce(sp.disbursed_amount_zar, 0) - c.committed_amount_zar, 2)
                                                             as settlement_variance_zar,

        case
            when sp.transfer_id is null
                then 'MISSING_SETTLEMENT'
            when sp.successful_payout_count > 1
                then 'DUPLICATE_SETTLEMENT'
            when abs(coalesce(sp.disbursed_amount_zar, 0) - c.committed_amount_zar) > 0.01
                then 'SETTLEMENT_VARIANCE'
            else 'RECONCILED'
        end                                                  as payout_recon_status,

        current_timestamp() as _dbt_updated_at

    from completed_transfers c
    left join successful_payouts sp on c.transfer_id = sp.transfer_id
    left join payout_attempts pa    on c.transfer_id = pa.transfer_id
)

select * from reconciled
