LINK_TEMPLATE = """
<a href="{{ link }}">{{ text }}</a>
"""

ELEMENT_TEMPLATE = """
{% for flag in flags %}
  {{ get_flag_html(flag) }}
{% endfor %}
"""

FLAG_TEMPLATE = """
<div class="pyagram-flag">
  <div class="pyagram-banner {% if is_curr_element %} curr-element {% endif %}">
    <!-- TODO -->
    <p>TODO</p>
    <!-- TODO -->
  </div>
  {{ get_element_html(this) }}
  {% if frame is not none %}
    {{ get_frame_html(frame) }}
  {% endif %}
</div>
"""

FRAME_TEMPLATE = """
<div class="pyagram-frame {% if is_curr_element %} curr-element {% endif %}">
  <p>
    {% if id == 0 %}
      Global Frame
    {% else %}
      Frame {{ id }} (parent: Frame {{ parent_id }})
    {% endif %}
  </p>
  <table>
    {% for key, value in bindings.items() %} <!-- TODO: Verify these show up in the right order! -->
      <tr>
        <td>{{ key }}</td>
        <td>{{ get_reference_html(value) }}</td>
      </tr>
    {% endfor %}
    {% if return_value is not none %}
      <tr>
        <td>Return value</td>
        <td>{{ get_reference_html(return_value) }}</td>
      </tr>
    {% endif %}
  </table>
</div>
{{ get_element_html(this) }}
"""
