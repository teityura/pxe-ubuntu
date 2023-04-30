#!/usr/bin/env python3
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader

def render_file(rendered, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)
    print(output_path)

def main():
    with open("hosts.json") as f:
        data = json.load(f)
        docker_host = data["docker_host"]
        pxe_clients = data["pxe_clients"]

    env = Environment(loader=FileSystemLoader("."))

    # conf ファイルを生成する
    templates = [
        ("templates/dnsmasq/default.j2", Path("templates_generated/dnsmasq/default")),
        ("templates/dnsmasq/grub.cfg.j2", Path("templates_generated/dnsmasq/grub.cfg")),
        ("templates/dnsmasq/pxe-dnsmasq.conf.j2", Path("templates_generated/dnsmasq/pxe-dnsmasq.conf")),
    ]
    for template_file_name, output_path in templates:
        template = env.get_template(template_file_name)
        rendered = template.render(docker_host=docker_host, pxe_clients=pxe_clients)
        render_file(rendered, output_path)

    # ホストごとに user-data を生成する
    template_file_name = "templates/httpd/user-data.j2"
    for pxe_client in pxe_clients:
        output_dir = Path("templates_generated", "httpd", "autoinstall", pxe_client['HOST_NAME'])
        output_path = output_dir / "user-data"
        template = env.get_template(template_file_name)
        rendered = template.render(docker_host=docker_host, pxe_client=pxe_client)
        render_file(rendered, output_path)
        open(output_dir / "meta-data", "w").close()

if __name__ == "__main__":
    main()
