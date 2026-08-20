{#
    Custom generic test: no_orphan_transfers

    A referential check with a tolerance. Strict relationships tests fail the
    entire build when a single late-arriving payout hasn't landed yet, which in
    a streaming remittance pipeline is normal rather than broken. This allows a
    configurable percentage of orphans before failing, so genuine breakage
    (a dropped partition, a bad join) still surfaces but ordinary lag doesn't
    page anyone at 3am.
#}

{% test no_orphan_transfers(model, column_name, to, field, max_orphan_pct=0.5) %}

with child as (

    select {{ column_name }} as fk_value
    from {{ model }}
    where {{ column_name }} is not null

),

parent as (

    select {{ field }} as pk_value
    from {{ to }}

),

orphans as (

    select c.fk_value
    from child c
    left join parent p
        on c.fk_value = p.pk_value
    where p.pk_value is null

),

summary as (

    select
        (select count(*) from orphans) as orphan_count,
        (select count(*) from child)   as total_count
)

select
    orphan_count,
    total_count,
    round(orphan_count * 100.0 / nullif(total_count, 0), 4) as orphan_pct
from summary
where round(orphan_count * 100.0 / nullif(total_count, 0), 4) > {{ max_orphan_pct }}

{% endtest %}
