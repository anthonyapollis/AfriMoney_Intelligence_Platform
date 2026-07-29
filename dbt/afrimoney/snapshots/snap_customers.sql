{% snapshot snap_customers %}

{{
  config(
    target_schema  = 'SNAPSHOTS',
    unique_key     = 'customer_id',
    strategy       = 'check',
    check_cols     = [
      'kyc_level',
      'customer_status',
      'risk_band',
      'customer_segment',
      'monthly_income_band',
      'is_marketing_opt_in'
    ],
    invalidate_hard_deletes = true,
    tags = ['snapshot', 'customers', 'scd2']
  )
}}

/*
  snap_customers — SCD Type 2 via dbt snapshot
  -----------------------------------------------
  Source : BRONZE.DIM_CUSTOMER (current row per customer)
  Tracks : KYC upgrades, status changes, risk re-banding, segment moves,
           income reclassification, marketing consent changes.

  dbt adds automatically:
    dbt_scd_id        — surrogate key for the snapshot version
    dbt_updated_at    — when dbt detected the change
    dbt_valid_from    — start of this version
    dbt_valid_to      — end of this version (NULL = current)
*/

select
    customer_id,
    business_key,

    -- Identity (immutable)
    age_years,
    gender,
    nationality,
    residence_country,
    preferred_language,
    mobile_number_token,
    email_hash,
    registration_datetime,
    registration_channel,
    acquisition_source,
    has_sa_id,
    has_passport,

    -- Mutable KYC & risk fields (check_cols above)
    kyc_level,
    kyc_completed_date,
    customer_status,
    risk_band,
    customer_segment,
    monthly_income_band,
    employer_type,
    is_marketing_opt_in,

    -- Metadata
    _loaded_at

from {{ source('bronze', 'dim_customer') }}
where is_current = true

{% endsnapshot %}
