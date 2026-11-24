# Security Control Hub roadmap

## Phase 1 - Local development baseline

- [x] Serve enabled controls, latest results, and check history through FastAPI.
- [x] Model control definitions and check records in PostgreSQL 17 with SQLAlchemy and Alembic.
- [x] Provide a local Compose database with a named volume and a health check.
- [x] Seed four synthetic control definitions for local development.
- [x] Declare Python 3.12 runtime and development dependencies.
- [x] Run SQLite API tests without PostgreSQL settings and lint the repository with Ruff.
- [x] Document local installation, migrations, seeding, and API startup.

## Phase 2 - Access to compliance evidence

- [ ] Define who may read control summaries and detailed evidence.
- [ ] Authenticate API callers and test authorization on evidence routes.
- [ ] Separate the API database role from migration and data-writing roles.

## Phase 3 - Check results and history

- [ ] Define evidence freshness, source validation, and handling of sensitive notes.
- [ ] Exercise check ingestion with synthetic data and test status ordering.
- [ ] Paginate the catalog and history, and optimize latest-status queries.
- [ ] Define how reviewers can retrieve evidence for retired controls.

## Phase 4 - Operations

- [ ] Run CI against a disposable PostgreSQL 17 database to verify migrations, constraints, and seed reruns.
- [ ] Add database readiness checks, structured logging, and service metrics.
- [ ] Package the API for deployment and document backup and recovery procedures.

## Planned DevOps and SRE roadmap

Phase 1 runs the API on the host and PostgreSQL in Docker Compose. All milestones below are planned.

### Docker and GitHub Actions

- [ ] Build a multi-stage Docker image that runs the API as a non-root user. Add it to local Compose with a loopback port binding and a container health check.
- [ ] Run Ruff, pytest, and PostgreSQL migration and seed checks on pull requests with GitHub Actions.
- [ ] Build the image, scan it with Trivy, and publish passing images to GitHub Container Registry (GHCR) with a commit SHA tag. Reproduce the build and test stages in Jenkins.

### Kubernetes, Helm, and Argo CD

- [ ] Deploy to a local Minikube cluster with a Deployment and Service. Configure Secrets, ConfigMaps, resource requests and limits, readiness and liveness probes, and persistent storage for PostgreSQL.
- [ ] Package the manifests as a Helm chart with environment-specific values. Test local Ingress, horizontal autoscaling, a rolling upgrade, and rollback to the previous release.
- [ ] Have Argo CD sync the chart from Git. Introduce drift in the local cluster, verify detection, and restore the declared configuration.

### Terraform and Ansible

- [ ] Use Terraform to provision an AWS development environment with VPC networking, IAM roles, ECR, EKS, and remote state. Set a budget alert and verify teardown of billable resources.
- [ ] Use Ansible playbooks to configure development hosts and their tooling. Run each playbook twice and verify the second run reports no changes.

### Monitoring and logging

- [ ] Collect request counts, errors, and latency with Prometheus. Build Grafana dashboards and verify Alertmanager routing with a simulated failure.
- [ ] Emit structured API logs with request IDs. Ship them to Loki with Grafana Alloy and use a request ID to trace a failed request without recording evidence payloads.

### SLOs and incident simulations

- [ ] Define availability and latency service-level indicators for control reads. Set service-level objectives (SLOs), a measurement window, and error-budget alerts. Exercise them under k6 load.
- [ ] In an isolated environment with synthetic data, simulate an API crash, a PostgreSQL outage, and a failed Kubernetes rollout. Record detection and recovery times and verify that control reads recover in each drill.
- [ ] Rehearse restoring a PostgreSQL backup. Use the drill results to update recovery runbooks and write incident reports with root causes and follow-up actions.
