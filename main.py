import os
import ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

TARGET_DIR = "."
OUTPUT_REPORT = "informe_iac.md"

def scan_iac_with_ai(file_path, file_content):
    """Sends infrastructure files to Ollama (Mistral) for IaC security auditing."""
    prompt = f"""
    Act as an expert Cloud Architect and Cybersecurity Auditor specialized in Infrastructure as Code (IaC) Security and DevSecOps.
    Analyze the following infrastructure configuration file for critical security vulnerabilities and bad practices.
    
    Look specifically for:
    1. Dangerous port exposures (e.g., SSH 22, RDP 3389, or databases exposed to 0.0.0.0/0).
    2. Containers running with root privileges (e.g., USER root or missing non-privileged user in Dockerfiles).
    3. Excessive permissions or lack of encryption (e.g., public S3 buckets, hardcoded access keys or secrets in plain environment variables).
    4. Use of outdated, insecure base images or the 'latest' tag in production.
    5. Missing resource limits or insecure privilege configurations in Kubernetes/Terraform.

    File to analyze ({file_path}):
    ```text
    {file_content}
    ```

    Provide a detailed structured report including:
    - Name of the misconfiguration or vulnerability found.
    - Risk level (High, Medium, Low).
    - Affected line or block.
    - Explanation of the risk in production/cloud environments.
    - Solution or recommended best practices to fix it.
    """

    try:
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

def main():
    console.print(Panel.fit("☁️ Starting IaC Security Validator (Ollama + Mistral)", style="bold magenta"))
    
    report_content = "# 📊 Global IaC Security Audit Report\n\n"
    report_content += "Infrastructure as Code Static Analysis powered by Local AI.\n\n---\n\n"

    scanned_files = 0
    valid_extensions = (".tf", ".yaml", ".yml", "Dockerfile")

    for root, _, files in os.walk(TARGET_DIR):
        if "venv" in root or ".git" in root or "assets" in root:
            continue
            
        for file in files:
            if file.endswith(valid_extensions) or file.lower() == "dockerfile":
                file_path = os.path.join(root, file)
                console.print(f"\n[yellow]🔍 Analyzing infrastructure:[/yellow] {file_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    
                    analysis = scan_iac_with_ai(file_path, file_content)
                    
                    report_content += f"## 📄 Configuration File: `{file_path}`\n\n"
                    report_content += analysis + "\n\n---\n\n"
                    scanned_files += 1

                except Exception as e:
                    console.print(f"[red]Error reading file {file_path}: {e}[/red]")

    if scanned_files > 0:
        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            f.write(report_content)

        console.print(f"\n[green]✅ IaC audit completed! {scanned_files} file(s) analyzed.[/green]")
        console.print(f"[green]📄 Report successfully generated at: {OUTPUT_REPORT}[/green]\n")

        console.print(Panel(Markdown(report_content), title="[bold blue]IaC Report Preview[/bold blue]", border_style="blue"))
    else:
        console.print("[yellow]⚠️ No valid infrastructure files (.tf, yaml, Dockerfile) found in the directory.[/yellow]")

if __name__ == "__main__":
    main()