{% snapshot snap_transfers %}

{{
  config(
    target_schema  = 'SNAPSHOTS',
    unique_key     = 'transfer_id',
    strategy       = 'check',
    check_cols     = [
      'transfer_status',
      'is_completed',
      'is_failed',
      'is_cancelled',
      'is_refunded',
      'is_suspected_fraud',
      'payment_attempts',
      'payout_attempts',
      'completion_minutes'
    ],
    invalidate_hard_deletes = true,
    tags = ['snapshot', 'transfers', 'scd2']
  )
}}

/*
  snap_transfers — SCD Type 2 via dbt snapshot
  -----------------------------------------------
  Source : BRONZE.FACT_REMITTANCE_TRANSFER
  Tracks : Status transitions (PENDING → PROCESSING → COMPLETED / FAILED),
           fraud flag changes, retry counts, completion time updates.

  Complements FACT_TRANSFER_STATUS_HISTORY (event log) by providing
  a clean before/after view of each state change with dbt_valid_from
  and dbt_valid_to timestamps.

  Use for: SLA breach analysis, fraud detection timing, refund audits,
           regulatory reporting on transfer lifecycle.
*/

select
    transfer_id,
    transfer_reference,
    business_key,
    sender_customer_id,
    recipient_id,
    corridor_code,
    send_country,
    receive_country,
    send_currency,
    receive_currency,
    channel,
    payment_method,
    payout_method,
    created_datetime,
    created_date_key,

    -- Mutable status fields (check_cols above)
    transfer_status,
    is_completed,
    is_failed,
    is_cancelled,
    is_refunded,
    is_suspected_fraud,
    payment_attempts,
    payout_attempts,
    completion_minutes,
    completed_datetime,

    -- Monetary (immutable after creation)
    send_amount_zar,
    receive_amount,
    transfer_fee_zar,
    gross_revenue_zar,
    net_revenue_zar,
    market_fx_rate,
    customer_fx_rate,
    fx_spread_pct,

    -- Flags (immutable)
    is_first_transfer,
    is_repeat_customer,

    -- Metadata
    _loaded_at

from {{ source('bronze', 'fact_remittance_transfer') }}

{% endsnapshot %}
