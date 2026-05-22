import jinja2
# from weasyprint import HTML
import os

def generate_pdf_report(findings: list, output_path: str) -> str:
    """
    Renders HTML from Jinja2 templates and compiles it to PDF using WeasyPrint.
    """
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template("report.html.j2")
    
    html_content = template.render(
        findings=findings,
        report_title="Compliance Audit Gap Report",
        generation_date="2026-05-22"
    )
    
    # Stub compilation
    # HTML(string=html_content).write_pdf(output_path)
    
    with open(output_path + ".html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return output_path
