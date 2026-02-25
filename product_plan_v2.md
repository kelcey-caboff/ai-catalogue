# AI Catalogue — Product Plan v2

## What we're building

A Django + PostgreSQL + Docker Compose platform for cataloguing AI use across the organisation. It sits alongside existing enterprise tools (Ardoq, Informatica, Atamis) and fills the gap specifically for AI products, models, and use cases.

### Goals
- Catalogue of assured tools/platforms
- Catalogue of tools in use and where models are deployed
- SRO and responsible owner tracking per product/tool
- Assurance documentation tracking (lightweight — links and status, not full workflow)
- CRM-style knowledge base for tools and products on the market
- Public-facing "nutrition label" front-end for transparency
- REST API for integration in/out with Ardoq, Informatica, and other systems

### Reference ontology
https://github.com/kelcey-caboff/ai-ontology — used as a "vibe-guide", not implemented to the letter. The SHACL validation and attestation workflow from that repo are out of scope.

---

## Technology decisions

| Concern | Decision |
|---|---|
| Framework | Django |
| Database | PostgreSQL |
| Infrastructure | Docker Compose (Django + PostgreSQL + Nginx) |
| API | Django REST Framework — API-first design |
| Front-end styling | GOV.UK Design System |
| Auth | Django built-in auth to start; SSO (django-allauth) is a later addition |
| Admin UI | Django admin for data entry (Phase 1); custom staff UI is Phase 2 |

---

## Data model

### Organisation
Represents government departments and vendors.

| Field | Type | Notes |
|---|---|---|
| name | CharField | |
| org_type | ChoiceField | Department / Vendor |
| website | URLField | optional |
| notes | TextField | optional |

### AIModel
The underlying model (LLM, classifier, embedding model, etc.).

| Field | Type | Notes |
|---|---|---|
| name | CharField | |
| version | CharField | |
| developer | FK → Organisation | the developer/publisher org |
| model_type | ChoiceField | LLM, Multimodal, Embedding, Classifier, Predictor, Anomaly Detector, Recommender, NER, Other |
| parameter_count | BigIntegerField | optional |
| context_window_size | IntegerField | optional (tokens) |
| training_cutoff_date | DateField | optional |
| training_includes_pii | BooleanField | |
| training_includes_govt_data | BooleanField | |
| explainability_level | ChoiceField | Black Box / Partial / Full |
| notes | TextField | optional |
| custom_attributes | JSONField | extensibility — arbitrary key/value pairs |

### AITool
A product, platform, or service that uses one or more AI models.

| Field | Type | Notes |
|---|---|---|
| name | CharField | |
| description | TextField | |
| vendor | FK → Organisation | |
| deployment_type | ChoiceField | Cloud / On-Premise / Hybrid |
| licensing_model | ChoiceField | Commercial / Open Source / In-House |
| product_type | ChoiceField | Product / Service / Platform |
| approval_status | ChoiceField | Pending / Approved / Rejected / Suspended / Under Review |
| models | M2M → AIModel | models employed by this tool |
| ardoq_link | URLField | optional — link to record in Ardoq |
| informatica_link | URLField | optional — link to dataset in Informatica |
| contract_link | URLField | optional — link to contract in Atamis |
| data_residency | CharField | optional |
| security_certification | CharField | optional |
| last_assessment_date | DateField | optional |
| notes | TextField | optional |
| custom_attributes | JSONField | extensibility |

### UseCase
A defined use of an AI tool within the organisation.

| Field | Type | Notes |
|---|---|---|
| title | CharField | |
| description | TextField | |
| tool | FK → AITool | |
| owning_department | FK → Organisation | |
| risk_level | ChoiceField | Low / Medium / High / Critical |
| autonomy_level | ChoiceField | Human-Driven / Human-in-Loop / Human-on-Loop / Autonomous |
| human_in_loop | BooleanField | |
| is_public_facing | BooleanField | |
| impacted_population | TextField | optional description |
| custom_attributes | JSONField | extensibility |

### Attestation (lightweight)
Tracks that an assessment has been done, with a link to evidence and a status.

| Field | Type | Notes |
|---|---|---|
| attestation_type | ChoiceField | DPIA / Bias Assessment / Security Review / Ethics Review / Legal Review / Other |
| subject_tool | FK → AITool | optional — links to tool |
| subject_usecase | FK → UseCase | optional — links to use case |
| status | ChoiceField | Pending / Completed / Expired |
| evidence_url | URLField | link to document (SharePoint, Confluence, etc.) |
| attestation_date | DateField | optional |
| expiry_date | DateField | optional |
| notes | TextField | optional |

### Role / SRO
Named responsible owner for a tool or use case.

| Field | Type | Notes |
|---|---|---|
| person_name | CharField | |
| email | EmailField | optional |
| role_type | ChoiceField | SRO / DPO / Security Officer / Ethics Officer / Technical Architect / Legal Counsel / Other |
| tool | FK → AITool | optional |
| use_case | FK → UseCase | optional |

---

## API design (Django REST Framework)

API-first. All data is accessible via a REST API. Supports both inbound and outbound integration with Ardoq, Informatica, and others.

### Endpoints (planned)

```
GET/POST   /api/v1/organisations/
GET/PUT    /api/v1/organisations/{id}/

GET/POST   /api/v1/models/
GET/PUT    /api/v1/models/{id}/

GET/POST   /api/v1/tools/
GET/PUT    /api/v1/tools/{id}/

GET/POST   /api/v1/usecases/
GET/PUT    /api/v1/usecases/{id}/

GET/POST   /api/v1/attestations/
GET/PUT    /api/v1/attestations/{id}/

GET/POST   /api/v1/roles/
GET/PUT    /api/v1/roles/{id}/
```

Authentication: token-based for API access. Public GET endpoints for public-facing data (read-only, no auth required).

---

## Front-end

### Public front-end (no auth)
- GOV.UK Design System
- Acts as a "nutrition label" for AI uses
- Browse tools, models, use cases
- Detail pages per tool showing: model used, use case, risk level, SRO, approval status, attestation summary

### Internal admin (Phase 1)
- Django admin, enhanced with sensible list displays, filters, and search
- Staff log in to create/update records

### Custom staff UI (Phase 2 — out of scope for now)
- Bespoke internal interface to replace Django admin

---

## Infrastructure

### Docker Compose services
- `web` — Django + Gunicorn
- `db` — PostgreSQL
- `nginx` — reverse proxy + static file serving

### Environment
- `.env` file for secrets (not committed)
- Static files served via Nginx
- Media files volume-mounted

---

## Phased delivery

### Phase 1 (initial build)
- [x] Docker Compose scaffold
- [x] Django project + PostgreSQL
- [x] Core data models (Organisation, AIModel, AITool, UseCase, Attestation, Role)
- [x] Django REST Framework API (all core entities)
- [x] Django admin configuration
- [x] GOV.UK Design System public front-end (list + detail views)
- [x] Basic token auth for API

### Phase 2 (later)
- [ ] SSO integration (django-allauth / SAML)
- [ ] Custom staff UI
- [ ] Ardoq push/pull integration
- [ ] Informatica push/pull integration
- [ ] Data import scripts (CSV/spreadsheet)
- [ ] Audit log / change history

---

## Out of scope
- SHACL validation / semantic web tooling
- Full attestation sign-off workflow (routing, approvals, notifications)
- Automated policy enforcement based on risk rules
- Data migration from existing systems at launch
