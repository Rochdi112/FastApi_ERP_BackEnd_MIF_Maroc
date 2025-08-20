from jinja2 import Environment, FileSystemLoader


def test_email_templates_render():
    env = Environment(loader=FileSystemLoader("app/templates"))
    for name in ("notification_information.html", "notification_alerte.html"):
        t = env.get_template(name)
        html = t.render(sujet="Info", message="OK")
        assert "<h1>Info</h1>" in html
        assert ">OK<" in html
