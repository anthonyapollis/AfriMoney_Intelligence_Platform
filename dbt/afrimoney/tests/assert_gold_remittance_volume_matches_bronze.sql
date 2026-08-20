/*
  Control-total reconciliation test.
  Sum(send_amount_zar) for completed transfers in the Silver staging layer
  must equal the sum of total_volume_zar in the Gold mart_remittance rollup,
  to the cent. A mismatch means the mart's grouping/join introduced fanout
  or dropped rows somewhere between Bronze and Gold — this is the same
  check finance runs manually at month-end sign-off, expressed as code.
  Passing test = 0 rows returned.
*/

with bronze_total as (
    select round(sum(send_amount_zar), 2) as total_zar
    from {{ ref('stg_transfers') }}
    where is_completed = true
),

gold_total as (
    select round(sum(total_volume_zar), 2) as total_zar
    from {{ ref('mart_remittance') }}
)

select
    b.total_zar as bronze_completed_volume_zar,
    g.total_zar as gold_mart_volume_zar,
    round(g.total_zar - b.total_zar, 2) as variance_zar
from bronze_total b
cross join gold_total g
where abs(g.total_zar - b.total_zar) > 0.01
