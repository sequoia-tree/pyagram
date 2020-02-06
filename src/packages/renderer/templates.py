STATE_TEMPLATE = """
<table>
  <tr>
    <td valign="top">
      {{ get_frame_html(global_frame) }}
    </td>
    <td valign="top">
      {% for object in memory_state %}
        {{ get_object_html(object) }}
      {% endfor %}
    </td>
  </tr>
</table>
"""

# TODO: This is how you *used to* do SVG stuff.
# STATE_TEMPLATE = """
# <div class="overlap-container">
#   <table id="state-table" class="overlap">
#     <tr>
#       <td valign="top">
#         {{ get_frame_html(global_frame) }}
#       </td>
#       <td valign="top">
#         {% for object in memory_state %}
#           {{ get_object_html(object) }}
#         {% endfor %}
#       </td>
#     </tr>
#   </table>
#   <svg id="svg-canvas" class="overlap" xmlns="http://www.w3.org/2000/svg">
#     <defs>
#       <marker id="circle" markerWidth="6.5" markerHeight="6.5" refX="5" refY="5">
#         <circle cx="5" cy="5" r="1.5" fill="black"/>
#       </marker>
#       <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="5" viewBox="0 0 10 10" orient="auto">
#         <path d="M0,0 L10,5 0,10 Z"/>
#       </marker>
#     </defs>
#     <g id="pointers" fill="none" stroke="black" stroke-width="1.5" marker-start="url(#circle)" marker-end="url(#arrowhead)"></g>
#   </svg>
# </div>
# """

ELEMENT_TEMPLATE = """
{% for flag in flags %}
  {{ get_flag_html(flag) }}
{% endfor %}
"""

FLAG_TEMPLATE = """
<div class="pyagram-flag m-3">
  <div class="pyagram-banner {% if is_curr_element %} curr-element {% endif %}">
    <table class="text-center font-family-monospace">
      <tr>
        {% for label, bindings in banner %}
          <td {% if bindings|length > 0 %} colspan="{{ bindings|length }}" {% endif %}>
            {{ label }}
          </td>
        {% endfor %}
      </tr>
      <tr>
        {% for i in range(banner|length) %}
          {% set label = banner[i][0] %}
          {% set bindings = banner[i][1] %}
          {% if bindings|length == 0 %}
            {% if i == 1 %}
              {% if i == banner|length - 1 %}
                <td class="text-left">()</td>
              {% else %}
                <td class="text-left">(</td>
              {% endif %}
            {% elif i == banner|length - 1 %}
              <td class="text-right">)</td>
            {% else %}
              <td class="text-left">,</td>
            {% endif %}
          {% else %}
            {% for binding in bindings %}
              <td class="pyagram-value {% if binding is none %} pyagram-placeholder {% endif %}">
                {% if binding is none %}
                  -
                {% else %}
                  {{ get_reference_html(binding) }}
                {% endif %}
              </td>
            {% endfor %}
          {% endif %}
        {% endfor %}
      </tr>
    </table>
  </div>
  {{ get_element_html(this) }}
  {% if frame is none %}
    <div class="pyagram-placeholder font-family-monospace">...</div>
  {% else %}
    {{ get_frame_html(frame) }}
  {% endif %}
</div>
"""

FRAME_TEMPLATE = """
<div class="pyagram-frame m-3 {% if is_curr_element %} curr-element {% endif %}">
  <div class="pyagram-frame-name">
    {{ name }} {% if parent is not none %} {{ get_parent_frame_html(parent) }} {% endif %}
  </div>
  <table class="ml-auto mr-0 font-family-monospace">
    {% for key, value in bindings.items() %}
      <tr>
        <td class="text-right">{{ key }}</td>
        <td class="pyagram-value text-left">{{ get_reference_html(value) }}</td>
      </tr>
    {% endfor %}
    {% if return_value is not none %}
      <tr>
        <td class="text-right font-family-sans-serif">Return value</td>
        <td class="pyagram-value text-left">{{ get_reference_html(return_value) }}</td>
      </tr>
    {% endif %}
  </table>
</div>
{{ get_element_html(this) }}
"""

LINK_TEMPLATE = """
<a href="{{ link }}">{{ text }}</a>
"""

POINTER_TEMPLATE = """
<span class="pyagram-placeholder reference-{{ id }}">
  -
</span>
"""

OBJECT_TEMPLATE = """
<div id="object-{{ id }}" class="pyagram-object m-3">
  {{ get_object_body_html(object) }}
</div>
"""

FUNCTION_TEMPLATE = """
function
<span class="ml-2 font-family-monospace">
  {% if lambda_id is none %}
    {{ name }}
  {% else %}
    {{ get_lambda_html(lambda_id) }}
  {% endif %}
  (
  {% for i in range(parameters|length) %}
    {% set parameter = parameters[i] %}
    {{ get_parameter_html(parameter) }}
    {% if i < parameters|length - 1 %}, {% endif %}
  {% endfor %}
  )
</span>
<div>
  {{ get_parent_frame_html(parent) }}
</div>
"""

BUILTIN_FUNCTION_TEMPLATE = """
function
<span class="ml-2 font-family-monospace">
  {{ name }}(...)
</span>
"""

LAMBDA_TEMPLATE = """
&#955;<sub>{{ lineno }}.{{ number }}</sub>
"""

# TODO: Put the {{ type }} on the same line as the boxes. Can you put the <table> in a <span>? Or make a <table> with one <tr> which contains two <td>s: the {{ type }}, and the boxes' <table>?
# TODO: px-2, or p-3?
ORDERED_COLLECTION_TEMPLATE = """
{{ type }}
<table class="pyagram-ordered-collection font-family-monospace" rules="cols">
  <tr>
    {% if elements|length == 0 %}
      TODO
    {% else %}
      {% for element in elements %}
        <td class="pyagram-collection-element px-2">{{ get_reference_html(element) }}</td>
      {% endfor %}
    {% endif %}
  </tr>
</table>
"""

UNORDERED_COLLECTION_TEMPLATE = """
TODO
"""

MAPPING_TEMPLATE = """
TODO
"""

ITERATOR_TEMPLATE = """
TODO
"""

GENERATOR_TEMPLATE = """
TODO
"""

OBJECT_FRAME_TEMPLATE = """
TODO
"""

OBJECT_REPR_TEMPLATE = """
<div class="font-family-monospace">
  {{ repr }}
</div>
"""

PARENT_FRAME_TEMPLATE = """
[parent: {{ parent_frame_name }}]
"""

PARAMETER_TEMPLATE = """
{{ name }}
{% if default is not none %}
  =<span class="pyagram-value">{{ get_reference_html(default) }}</span>
{% endif %}
"""

# TODO: Figure out how you plan to do the print output.
PRINT_TEMPLATE = """
<div class="font-family-monospace">
  {{ print_output }}
</div>
"""
