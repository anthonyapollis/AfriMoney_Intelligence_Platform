{{
  config(
    materialized = 'table',
    tags         = ['silver', 'intermediate', 'reconciliation'],
    cluster_by   = ['business_key', 'created_month']
  )
}}

/*
  int_payment_reconciliation
  Reconciles each transfer's committed collection amount (send amount + fee,
  from FACT_REMITTANCE_TRANSFER) against what FACT_PAYMENT actually recorded
  as successfully charged. Only the SUCCESS attempt should count toward
  collection — declined/failed retries must never be summed in, or collection
  totals get inflated.
  Grain: one row per transfer_id.
*/

with transfers as (
    select
        transfer_id,
        business_key,
        corridor_code,
        created_month,
        transfer_status,
        is_completed,
        send_amount_zar,
        transfer_fee_zar,
        vat_zar,
        (send_amount_zar + transfer_fee_zar) as expected_collection_zar
    from {{ ref('stg_transfers') }}
),

successful_payments as (
    select
        transfer_id,
        sum(total_charged_zar)  as actual_collection_zar,
        count(*)                as successful_payment_count
    from {{ source('bronze', 'fact_payment') }}
    where payment_status = 'SUCCESS'
    group by 1
),

payment_attempts as (
    select
        transfer_id,
        count(*)                                          as total_payment_attempts_recorded,
        sum(iff(payment_status = 'DECLINED', 1, 0))        as declined_attempt_count,
        sum(iff(payment_status = 'FAILED', 1, 0))          as failed_attempt_count
    from {{ source('bronze', 'fact_payment') }}
    group by 1
),

reconciled as (
    select
        t.transfer_id,
        t.business_key,
        t.corridor_code,
        t.created_month,
        t.transfer_status,
        t.is_completed,

        t.expected_collection_zar,
        coalesce(sp.actual_collection_zar, 0)               as actual_collection_zar,
        coalesce(sp.successful_payment_count, 0)            as successful_payment_count,
        coalesce(pa.total_payment_attempts_recorded, 0)     as total_payment_attempts_recorded,
        coalesce(pa.declined_attempt_count, 0)              as declined_attempt_count,
        coalesce(pa.failed_attempt_count, 0)                as failed_attempt_count,

        round(coalesce(sp.actual_collection_zar, 0) - t.expected_collection_zar, 2)
                                                             as payment_variance_zar,

        case
            when t.is_completed and sp.transfer_id is null
                then 'MISSING_PAYMENT'
            when sp.successful_payment_count > 1
                then 'DUPLICATE_SUCCESSFUL_PAYMENT'
            when not t.is_completed and sp.transfer_id is not null
                then 'COLLECTED_ON_INCOMPLETE_TRANSFER'
            when t.is_completed
                 and abs(coalesce(sp.actual_collection_zar, 0) - t.expected_collection_zar) > 0.01
                then 'AMOUNT_MISMATCH'
            else 'RECONCILED'
        end                                                  as payment_recon_status,

        current_timestamp() as _dbt_updated_at

    from transfers t
    left join successful_payments sp on t.transfer_id = sp.transfer_id
    left join payment_attempts pa    on t.transfer_id = pa.transfer_id
)

select * from reconciled
