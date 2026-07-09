# AutomationLab

A production-grade platform engineering environment I run at home.

I operate this lab the way a real platform team operates production: everything is monitored, backed up, restore-tested, and automated. Every change goes through Git and a pull request. Every secret comes from a vault. Every pipeline is code.

I built it to sharpen my platform engineering skills, and I write everything down so anyone can follow along, whether you're learning this stuff yourself or just curious how it fits together.

## The stack

- **Virtualization:** 5-node Proxmox cluster, high availability and live migration *(Completed)*
- **Kubernetes:** K3s with Argo CD for GitOps *(Completed)*
- **CI/CD:** Jenkins *(Completed)*, Gitea Actions *(In Progress)*
- **Infrastructure as Code:** Terraform, Ansible, Packer *(Completed)*
- **Secrets & identity:** HashiCorp Vault, Active Directory, Entra ID SSO, enterprise PKI, MFA *(Completed)*
- **Monitoring:** Zabbix *(Completed)*, Prometheus & Grafana *(Planned)*
- **Source & registry:** self-hosted Gitea *(Completed)*
- **AI/LLM:** local inference on my own GPU for self-healing and ops tooling *(In Progress)*

## Write-ups

I document each system the same way: what problem it solved, how it works, the decisions I made and why, and what I learned along the way.

- **[The Self-Service Server Build Pipeline](writeups/provisioning-pipeline-writeup.md)** — one click to provision a fully configured, monitored VM from nothing, and cleanly tear it back down *(Completed)*
- *(more coming as I write them up)*

## A note on how this is built

I lean on AI tooling heavily in this lab, but with a firm rule: I verify everything before I trust it. Nothing gets committed straight to main, nothing ships without evidence it works. The goal is to move fast without cutting the corners that matter.
