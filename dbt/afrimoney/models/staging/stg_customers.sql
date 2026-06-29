{{
  config(
    materialized = 'view',
    tags         = ['silver', 'staging', 'customers']
  )
}}

with source as (
    select * from {{ source('bronze', 'dim_customer') }}
),

staged as (
    select
        customer_sk,
        customer_id,
        business_key,

        -- Demographics (no PII — tokens/hashes only)
        age_years,
        gender,
        nationality,
        residence_country,
        preferred_language,
        mobile_number_token,
        email_hash,

        -- Onboarding
        registration_datetime::timestamp_ntz        as registered_at,
        date_trunc('month', registration_datetime)::date as registration_month,
        registration_channel,

        -- KYC & Risk
        kyc_level,
        kyc_completed_date,
        customer_status,
        risk_band,

        -- Segmentation
        customer_segment,
        monthly_income_band,
        employer_type,

        -- Flags
        has_sa_id,
        has_passport,
        is_marketing_opt_in,
        acquisition_source,

        -- SCD2 fields
        scd_version,
        scd_start_date,
        scd_end_date,
        is_current,

        -- Derived
        datediff('day', registration_datetime, current_timestamp())  as days_since_registration,
        (kyc_level in ('LEVEL_2','LEVEL_3'))::boolean                as is_fully_verified,
        (customer_status = 'ACTIVE')::boolean                        as is_active

    from source
)

select * from staged
