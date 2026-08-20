{#
    Custom generic test: completeness_within_tolerance

    Reconciliation completeness is a two-sided check — unlike almost every other
    metric in the platform, being ABOVE target is just as broken as being below.
    100.4% collection means duplicate charges went out and customers are owed
    money back; 99.6% means revenue was never collected. dbt ships nothing that
    expresses "must sit inside a band", so this test does.

    Usage in a schema .yml:

        columns:
          - name: collection_completeness_pct
            data_tests:
              - completeness_within_tolerance:
                  lower_bound: 98
                  upper_bound: 102
#}

{% test completeness_within_tolerance(model, column_name, lower_bound=99, upper_bound=101) %}

with validation as (

    select
        {{ column_name }} as completeness_value
    from {{ model }}
    where {{ column_name }} is not null

),

failures as (

    select
        completeness_value
    from validation
    where completeness_value < {{ lower_bound }}
       or completeness_value > {{ upper_bound }}

)

select * from failures

{% endtest %}
