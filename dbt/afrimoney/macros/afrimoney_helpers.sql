{#
    Reusable AfriMoney transformation helpers.
    Keeping these in macros rather than repeating the SQL means a change to,
    say, how we round money happens in exactly one place.
#}


{#
    Money is stored as NUMBER(18,6) upstream because FX conversion needs the
    precision, but every reported figure must settle to whole cents — otherwise
    the reconciliation models chase sub-cent drift that isn't a real break.
#}
{% macro zar(column_expression) -%}
    round({{ column_expression }}, 2)
{%- endmacro %}


{#
    Safe percentage. Snowflake's div0 handles the divide-by-zero, but we also
    want a genuine NULL (not 0) when the denominator is NULL, so a missing
    denominator doesn't masquerade as "0% and healthy" on a dashboard.
#}
{% macro safe_pct(numerator, denominator, scale=100) -%}
    case
        when {{ denominator }} is null or {{ denominator }} = 0 then null
        else round(({{ numerator }} / {{ denominator }}) * {{ scale }}, 4)
    end
{%- endmacro %}


{#
    Corridor codes are stored as 'ZA-ZW' style strings. These parse the leg out
    without every model re-implementing the split_part offsets.
#}
{% macro corridor_send_country(column_expression='corridor_code') -%}
    split_part({{ column_expression }}, '-', 1)
{%- endmacro %}

{% macro corridor_receive_country(column_expression='corridor_code') -%}
    split_part({{ column_expression }}, '-', 2)
{%- endmacro %}


{#
    Dev-run row limiting.

    A full build over 5M+ transfers on an XS warehouse is slow and burns credits
    for no reason during development. This clamps non-prod builds to a recent
    window; prod builds get everything. Applied in the incremental models' base
    CTEs. Controlled by the `dev_lookback_months` var so it can be widened when
    a developer genuinely needs more history.
#}
{% macro limit_data_in_dev(column_name='created_at') -%}
    {%- if target.name != 'prod' -%}
        where {{ column_name }} >= dateadd(
            month,
            -{{ var('dev_lookback_months', 3) }},
            current_date()
        )
    {%- endif -%}
{%- endmacro %}


{#
    Standard incremental predicate.

    Late-arriving data is a real problem on this platform: a transfer created on
    the 30th can have its payout settle days later, which updates the row after
    we've already loaded it. Filtering on `> max(created_at)` alone would miss
    those updates forever. Instead we re-scan a lookback window and let the merge
    strategy overwrite anything that changed inside it.
#}
{% macro incremental_lookback_filter(column_name='created_at') -%}
    {% if is_incremental() %}
        where {{ column_name }} >= (
            select coalesce(
                dateadd(day, -{{ var('incremental_lookback_days', 7) }}, max({{ column_name }})),
                '1900-01-01'::timestamp_ntz
            )
            from {{ this }}
        )
    {% endif %}
{%- endmacro %}
