{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'reconciliation'],
    cluster_by    = ['business_key', 'created_month'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_reconciliation
  Monthly corridor-level control-total reconciliation: money committed
  (FACT_REMITTANCE_TRANSFER) vs money collected (FACT_PAYMENT) vs money
  disbursed (FACT_PAYOUT). This is the sign-off surface finance/ops use each
  month — collection completeness, settlement completeness, and a single
  "reconciliation breaks" count that should trend to zero.
  Grain: business_key + corridor_code + created_month
*/

with payment_recon as (
    select
        business_key,
        corridor_code,
        created_month,
        count(*)                                                     as transfer_count,
        sum(expected_collection_zar)                                 as total_expected_collection_zar,
        sum(actual_collection_zar)                                   as total_actual_collection_zar,
        sum(payment_variance_zar)                                    as total_payment_variance_zar,
        sum(iff(payment_recon_status = 'MISSING_PAYMENT', 1, 0))     as missing_payment_count,
        sum(iff(payment_recon_status = 'DUPLICATE_SUCCESSFUL_PAYMENT', 1, 0))
                                                                      as duplicate_payment_count,
        sum(iff(payment_recon_status = 'AMOUNT_MISMATCH', 1, 0))     as payment_amount_mismatch_count
    from {{ ref('int_payment_reconciliation') }}
    where is_completed = true
    group by 1, 2, 3
),

payout_recon as (
    select
        business_key,
        corridor_code,
        created_month,
        count(*)                                                     as completed_transfer_count,
        sum(committed_amount_zar)                                    as total_committed_amount_zar,
        sum(disbursed_amount_zar)                                    as total_disbursed_amount_zar,
        sum(settlement_variance_zar)                                 as total_settlement_variance_zar,
        sum(iff(payout_recon_status = 'MISSING_SETTLEMENT', 1, 0))   as missing_settlement_count,
        sum(iff(payout_recon_status = 'DUPLICATE_SETTLEMENT', 1, 0)) as duplicate_settlement_count,
        sum(iff(payout_recon_status = 'SETTLEMENT_VARIANCE', 1, 0))  as settlement_variance_count
    from {{ ref('int_payout_reconciliation') }}
    group by 1, 2, 3
),

joined as (
    select
        coalesce(pay.business_key,  po.business_key)    as business_key,
        coalesce(pay.corridor_code, po.corridor_code)   as corridor_code,
        coalesce(pay.created_month, po.created_month)   as created_month,

        -- Collection side (customer payment -> platform)
        coalesce(pay.transfer_count, 0)                  as transfer_count,
        coalesce(pay.total_expected_collection_zar, 0)   as total_expected_collection_zar,
        coalesce(pay.total_actual_collection_zar, 0)     as total_actual_collection_zar,
        coalesce(pay.total_payment_variance_zar, 0)      as total_payment_variance_zar,
        coalesce(pay.missing_payment_count, 0)           as missing_payment_count,
        coalesce(pay.duplicate_payment_count, 0)         as duplicate_payment_count,
        coalesce(pay.payment_amount_mismatch_count, 0)   as payment_amount_mismatch_count,
        div0(pay.total_actual_collection_zar, pay.total_expected_collection_zar) * 100
                                                          as collection_completeness_pct,

        -- Settlement side (platform -> recipient partner network)
        coalesce(po.completed_transfer_count, 0)         as completed_transfer_count,
        coalesce(po.total_committed_amount_zar, 0)       as total_committed_amount_zar,
        coalesce(po.total_disbursed_amount_zar, 0)       as total_disbursed_amount_zar,
        coalesce(po.total_settlement_variance_zar, 0)    as total_settlement_variance_zar,
        coalesce(po.missing_settlement_count, 0)         as missing_settlement_count,
        coalesce(po.duplicate_settlement_count, 0)       as duplicate_settlement_count,
        coalesce(po.settlement_variance_count, 0)        as settlement_variance_count,
        div0(po.total_disbursed_amount_zar, po.total_committed_amount_zar) * 100
                                                          as settlement_completeness_pct,

        -- Single roll-up KPI for the monthly sign-off view
        (coalesce(pay.missing_payment_count, 0)
         + coalesce(pay.duplicate_payment_count, 0)
         + coalesce(pay.payment_amount_mismatch_count, 0)
         + coalesce(po.missing_settlement_count, 0)
         + coalesce(po.duplicate_settlement_count, 0)
         + coalesce(po.settlement_variance_count, 0))    as total_reconciliation_breaks,

        current_timestamp()                              as _dbt_updated_at

    from payment_recon pay
    full outer join payout_recon po
        on  pay.business_key   = po.business_key
        and pay.corridor_code  = po.corridor_code
        and pay.created_month  = po.created_month
)

select * from joined
