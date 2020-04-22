STATE_TEMPLATE = """
<div class="overlap-wrapper">
  <table class="overlap border-collapse" id="pyagram-state-table">
    <tr>
      <td class="align-top">
        {{ get_frame_html(global_frame) }}
      </td>
      <td class="align-top pl-5">
        {% for object in memory_state %}
          {{ get_object_html(object) }}
        {% endfor %}
      </td>
    </tr>
  </table>
  <svg class="overlap" id="pyagram-svg-canvas" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <marker id="circle" markerWidth="6.5" markerHeight="6.5" refX="5" refY="5">
        <circle cx="5" cy="5" r="1.5" fill="black"/>
      </marker>
      <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="3" refY="5" viewBox="0 0 10 10" orient="auto">
        <path d="M0,0 L10,5 0,10 Z"/>
      </marker>
    </defs>
    <g id="pointers" fill="none" stroke="black" stroke-width="1.5" marker-start="url(#circle)" marker-end="url(#arrowhead)"/>
  </svg>
</div>
"""

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
<div class="pyagram-frame {% if frame_type == 'function' %} mx-3 {% else %} mr-3 {% endif %} my-3 {% if is_curr_element %} curr-element {% endif %}">
  <div class="pyagram-frame-name">
    {% if frame_type == 'function' %}
      {{ name }}
    {% elif frame_type == 'generator' %}
      generator <span class="font-family-monospace">{{ name }}</span>
    {% elif frame_type == 'class' %}
      class <span class="font-family-monospace">{{ name }}</span>
    {% elif frame_type == 'instance' %}
      <span class="font-family-monospace">{{ name }}</span> instance
    {% endif %} {{ get_parent_frame_html(parents, monospace=(frame_type == 'class' or frame_type == 'instance')) }}
  </div>
  <table class="ml-auto mr-0 font-family-monospace">
    {% for key, value in bindings.items() %}
      <tr>
        <td class="text-right">{{ key }}</td>
        <td class="pyagram-value pyagram-frame-value text-left">{{ get_reference_html(value) }}</td>
      </tr>
    {% endfor %}
    {% if return_value is not none %}
      <tr>
        <td class="text-right font-family-sans-serif">
        {% if frame_type == 'generator' %}
          Yield value
        {% else %}
          Return value
        {% endif %}
        </td>
        <td class="pyagram-value pyagram-frame-value text-left">{{ get_reference_html(return_value) }}</td>
      </tr>
    {% endif %}
  </table>
</div>
{{ get_element_html(this) }}
"""

META_REFERENCE_TEMPLATE = """
<span class="pyagram-{{ cls }}">
  {{ text }}
</span>
"""

PLAINTEXT_TEMPLATE = """
{% if monospace %}
  <span class="font-family-monospace">{{ text }}</span>
{% else %}
  {{ text }}
{% endif %}
"""

POINTER_TEMPLATE = """
<span class="pyagram-placeholder pyagram-reference font-family-monospace reference-{{ id }}">
  -
</span>
"""

OBJECT_TEMPLATE = """
<div id="object-{{ id }}" class="pyagram-object m-3">
  {{ get_object_body_html(object) }}
</div>
"""

FUNCTION_TEMPLATE = """
{% if is_gen_func %}
  generator function
{% else %}
  function
{% endif %}
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
  {{ get_parent_frame_html([parent]) }}
</div>
"""

BUILTIN_FUNCTION_TEMPLATE = """
function
<span class="ml-2 font-family-monospace">
  {{ name }}(...)
</span>
"""

LAMBDA_TEMPLATE = """
&#955;
<sub>
  {{ lineno }}
  {% if not single %}
    #{{ number }}
  {% endif %}
</sub>
"""

ORDERED_COLLECTION_TEMPLATE = """
{% if elements|length == 0 %}
  empty {{ type }}
{% else %}
  <div class="d-flex flex-row align-items-center">
    <div>{{type}}</div>
    <table class="pyagram-ordered-collection border-collapse ml-1 font-family-monospace" rules="cols">
    <tr>
      {% for element in elements %}
        <td class="pyagram-collection-element px-2">{{ get_reference_html(element) }}</td>
      {% endfor %}
    </tr>
  </table>
  </div>
{% endif %}
"""

UNORDERED_COLLECTION_TEMPLATE = """
{% if elements|length == 0 %}
  empty {{ type }}
{% else %}
  <div class="d-flex flex-row align-items-center">
    <div>{{type}}</div>
    <table class="pyagram-unordered-collection ml-1 font-family-monospace">
    <tr>
      {% for element in elements %}
        <td class="pyagram-collection-element px-2">{{ get_reference_html(element) }}</td>
      {% endfor %}
    </tr>
  </table>
  </div>
{% endif %}
"""

MAPPING_TEMPLATE = """
{% if items|length == 0 %}
  empty {{ type }}
{% else %}
  <div class="d-flex flex-row align-items-center">
    <div>{{type}}</div>
    <table class="pyagram-mapping border-collapse ml-1 font-family-monospace" rules="cols">
    <tr>
      {% for item in items %}
        <td class="pyagram-mapping-key px-2 text-center">{{ get_reference_html(item[0]) }}</td>
      {% endfor %}
    </tr>
    <tr>
      {% for item in items %}
        <td class="pyagram-mapping-value px-2 text-center">{{ get_reference_html(item[1]) }}</td>
      {% endfor %}
    </tr>
  </table>
  </div>
{% endif %}
"""

ITERATOR_TEMPLATE = """
iterator over <span class="pyagram-value">{{ get_reference_html(object) }}</span>
{% if annotation is not none %}
  <span> {{ annotation }}</span>
{% endif %}
<div>[next index: {{ index }}]</div>
"""

# TODO: Reconsider how you display these.
OBJECT_REPR_TEMPLATE = """
<div class="font-family-monospace">
  {{ repr }}
</div>
"""

PARENT_FRAME_TEMPLATE = """
{% if parents|length == 0 %}
{% elif parents|length == 1 %}
  [parent: {{ parents[0] }}]
{% else %}
  [parents: {% for i in range(parents|length - 1) %}{{ parents[i] }}, {% endfor %}{{ parents[-1] }}]
{% endif %}
"""

PARAMETER_TEMPLATE = """
{{ name }}
{% if default is not none %}
  =<span class="pyagram-value">{{ get_reference_html(default) }}</span>
{% endif %}
"""

PRINT_TEMPLATE = """
{% for line in print_output %}
  <div class="print-output {% if is_exception %} pyagram-exception {% endif %} font-family-monospace">
    {{ line }}
  </div>
{% endfor %}
"""
