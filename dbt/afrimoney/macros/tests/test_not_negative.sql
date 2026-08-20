{#
    Custom generic test: not_negative

    Applies to any monetary or count column that has no legitimate negative
    interpretation. Deliberately allows zero and ignores NULL — NULL-ness is the
    job of not_null, and conflating the two makes failures harder to read.
#}

{% test not_negative(model, column_name) %}

select
    {{ column_name }} as offending_value
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
