{{
  config(
    materialized  = 'table',
    tags          = ['gold', 'mart', 'lending', 'mukuru'],
    cluster_by    = ['origination_month'],
    post_hook     = "GRANT SELECT ON {{ this }} TO ROLE AFRIMONEY_ANALYST"
  )
}}

/*
  mart_loans_mukuru
  Mukuru Fast Loan origination, repayment, and delinquency analytics.
  Grain: origination_month + loan_purpose + risk_band
  Note: Mukuru-only product; no Mama Money equivalent.
*/

with applications as (
    select
        to_varchar(date_trunc('month', application_datetime), 'YYYY-MM') as origination_month,
        loan_purpose,
        risk_band,
        count(*)                                                    as total_applications,
        count(case when decision='APPROVED' then 1 end)            as approved_count,
        count(case when decision='REJECTED' then 1 end)            as rejected_count,
        div0(
            count(case when decision='APPROVED' then 1 end),
            count(*)
        ) * 100                                                     as approval_rate_pct,
        sum(case when decision='APPROVED' then principal_zar else 0 end) as total_disbursed_zar,
        avg(case when decision='APPROVED' then principal_zar else null end) as avg_loan_size_zar,
        avg(case when decision='APPROVED' then interest_rate else null end) as avg_interest_rate,
        avg(probability_of_default)                                as avg_pd_score,
        count(case when loan_status='DEFAULTED' then 1 end)        as defaulted_loans,
        count(case when loan_status='WRITTEN_OFF' then 1 end)      as written_off_loans,
        sum(case when days_past_due > 0 then 1 else 0 end)        as loans_with_arrears,
        avg(days_past_due)                                         as avg_dpd
    from {{ source('bronze', 'fact_loan_application') }}
    where business_key = 'MKR'
    group by 1, 2, 3
),

repayments as (
    select
        to_varchar(date_trunc('month', repayment_date), 'YYYY-MM') as repayment_month,
        sum(amount_paid_zar)                                        as total_collected_zar,
        sum(case when is_on_time then amount_paid_zar else 0 end)  as on_time_collected_zar,
        count(*)                                                    as repayment_events,
        div0(
            sum(case when is_on_time then amount_paid_zar else 0 end),
            sum(amount_paid_zar)
        ) * 100                                                     as on_time_collection_rate
    from {{ source('bronze', 'fact_loan_repayment') }}
    group by 1
)

select
    a.origination_month,
    a.loan_purpose,
    a.risk_band,
    a.total_applications,
    a.approved_count,
    a.rejected_count,
    a.approval_rate_pct,
    a.total_disbursed_zar,
    a.avg_loan_size_zar,
    a.avg_interest_rate,
    a.avg_pd_score,
    a.defaulted_loans,
    a.written_off_loans,
    a.loans_with_arrears,
    a.avg_dpd,
    div0(a.defaulted_loans, a.approved_count) * 100 as default_rate_pct,
    coalesce(r.total_collected_zar,     0)  as total_collected_zar,
    coalesce(r.on_time_collection_rate, 0)  as on_time_collection_rate,
    -- IFRS 9 ECL indicator: avg_pd * avg_loan_size * LGD assumption 45%
    round(a.avg_pd_score * a.avg_loan_size_zar * 0.45, 2) as ifrs9_ecl_per_loan_zar,
    current_timestamp() as _dbt_updated_at
from applications a
left join repayments r on a.origination_month = r.repayment_month
