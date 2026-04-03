## Industrial IoT Cloud-Native Transformation
Architecting the Bridge between Legacy Manufacturing & Generative AI

### 1. Executive Summary
This project demonstrates a production-grade transition from legacy industrial middleware to a Cloud-Native AI Ecosystem. Designed with the requirements of a global industrial leader in mind, the architecture focuses on high availability, automated edge-to-cloud data flow, and leveraging Generative AI for predictive maintenance insights.

Key Achievements:

Zero-Touch Provisioning: Automated edge gateway setup using Ansible.

Self-Healing Infrastructure: Production-ready EKS cluster managed via Terraform.

GenAI Integration: RAG-based (Retrieval-Augmented Generation) assistant for real-time equipment troubleshooting.


### 2. System Architecture

<img width="1561" height="5067" alt="IoT Middleware to GenAI" src="https://github.com/user-attachments/assets/7f06a1c9-81c8-4d04-bffb-83f2f7472078" />

### 3. Technical Stack & Implementation
Infrastructure as Code (IaC): Terraform scripts for VPC, EKS, and IAM Role definitions.

Configuration Management: Ansible playbooks for RHEL/Ubuntu hardening and Middleware (Apache) deployment.

Orchestration: Kubernetes manifests including Helm charts, HPA (Horizontal Pod Autoscaling), and Ingress Controllers.

Generative AI: Python-based RAG pipeline using LangChain and Google Gemini API to process sensor logs.

### 4. Architectural Decision Records (ADR)
As a Senior Architect, I prioritized the following patterns:

Security First: All data in transit is encrypted via TLS, and the EKS cluster uses Private Subnets to minimize the attack surface.

FinOps Strategy: Implemented AWS Tagging and Auto-Scaling policies to ensure the environment scales down during off-peak hours, reducing waste by an estimated 15%.

Observability: Integrated Prometheus-style metrics to monitor the health of the containerized middleware.

### 5. How to Deploy (Quick Start)

**Prerequisites**
AWS CLI & Terraform installed.

A valid Google AI Studio API Key (for Gemini).

Ansible 2.15+.

**Steps**
Provision Infrastructure:

cd terraform
terraform init && terraform apply -auto-approve


Configure Edge Node:

cd ansible
ansible-playbook -i inventory setup-edge.yml

Deploy to Kubernetes:

kubectl apply -f kubernetes/manifests/

### 6. Future Roadmap
[ ] Integration with Snowflake for long-term Data Lake storage.

[ ] Multi-region failover for the EKS control plane.

[ ] Fine-tuning LLM models on specific industrial proprietary logs.

### 7. Contact & Professional Profile
Satyaki Sinha

Certifications: CKA, Google GenAI Leader, DevOps Practitioner.

Current Location: Peterborough, UK.

Connect: www.linkedin.com/in/satyaki-sinha | stksinha@gmail.com
