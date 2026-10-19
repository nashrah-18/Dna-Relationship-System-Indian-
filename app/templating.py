from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
    auto_reload=True,
    cache_size=0
)

def render_template(template_name: str, **context) -> str:
    template = env.get_template(template_name)
    return template.render(**context)