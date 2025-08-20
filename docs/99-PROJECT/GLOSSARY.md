---
title: "ERP MIF Maroc - Glossary of Terms"
path: "docs/99-PROJECT/GLOSSARY.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["glossary", "definitions", "terminology", "business-domain"]
---

# ERP MIF Maroc - Glossary of Terms

## Overview

This glossary defines key terms, concepts, and terminology used throughout the ERP MIF Maroc system. Understanding these terms is essential for effective communication among stakeholders, developers, and users of the system.

---

## A

**Admin (Administrator)**
: System administrator with full access to all features and configuration settings. Can manage users, system settings, and have oversight of all business operations.

**Affectée (Assigned)**
: Status of an intervention that has been assigned to a specific technician but work has not yet begun.

**Alembic**
: Database migration tool used with SQLAlchemy to manage schema changes and database versioning.

**API (Application Programming Interface)**
: Set of protocols and tools for building software applications. The ERP system provides a RESTful API for frontend and external system integration.

**Archivée (Archived)**
: Final status for interventions that have been completed and moved to historical storage for record-keeping purposes.

---

## B

**bcrypt**
: Cryptographic hashing function used for securely storing user passwords in the database.

**Bearer Token**
: Authentication method where the client sends a token (JWT) in the HTTP Authorization header as "Bearer {token}".

**Business Logic**
: The part of the application that encodes real-world business rules and determines how data can be created, stored, and changed.

---

## C

**Client**
: External organization or company that owns equipment and requests maintenance interventions. Clients have limited access to view their own equipment and interventions.

**Clôturée (Closed)**
: Status indicating that an intervention has been completed successfully and all work has been finished.

**CORS (Cross-Origin Resource Sharing)**
: Mechanism that allows restricted resources on a web page to be requested from another domain outside the domain from which the first resource was served.

**Corrective Maintenance**
: Type of intervention performed to fix equipment that has failed or is malfunctioning.

**CRUD (Create, Read, Update, Delete)**
: Basic operations that can be performed on data in the system.

**Criticité (Criticality)**
: Classification of equipment based on its importance to operations (critique, haute, normale, basse).

---

## D

**Database URL**
: Connection string that specifies how to connect to the PostgreSQL database, including credentials and connection parameters.

**Docker Compose**
: Tool for defining and running multi-container Docker applications. Used for development environment setup.

**Document**
: File attachment related to an intervention, such as photos, reports, manuals, or certificates.

**Domain Model**
: Conceptual model that describes the business domain and the relationships between business entities.

---

## E

**En Attente (On Hold)**
: Intervention status indicating work has been paused, typically waiting for parts, authorization, or external dependencies.

**En Cours (In Progress)**
: Status indicating that an intervention is actively being worked on by a technician.

**Enum (Enumeration)**
: Data type consisting of a set of named values representing different options or states.

**Équipement (Equipment)**
: Industrial machinery or equipment owned by clients that requires maintenance and can be the subject of interventions.

**ERP (Enterprise Resource Planning)**
: Business management software that integrates various business processes and functions into a unified system.

---

## F

**FastAPI**
: Modern, fast web framework for building APIs with Python, used as the foundation for the ERP backend.

**Foreign Key (FK)**
: Database constraint that maintains referential integrity between tables by referencing the primary key of another table.

---

## G

**Glossary**
: Alphabetical list of terms with explanations, providing a common vocabulary for all stakeholders.

---

## H

**Hashed Password**
: Encrypted version of a user's password stored in the database for security purposes.

**Historique (History/Audit Trail)**
: Complete record of all changes made to an intervention, including who made changes and when.

**HTTP Status Code**
: Three-digit code returned by web servers to indicate the result of an HTTP request (e.g., 200 OK, 404 Not Found).

---

## I

**Intervention**
: Core business entity representing a maintenance work order for equipment, including all details about the work to be performed.

**Intervention Type**
: Classification of maintenance work: corrective, preventive, ameliorative, or diagnostic.

---

## J

**JSON (JavaScript Object Notation)**
: Lightweight data interchange format used for API requests and responses.

**JWT (JSON Web Token)**
: Compact, URL-safe means of representing claims between parties, used for authentication and authorization.

---

## K

**KPI (Key Performance Indicator)**
: Measurable values that demonstrate how effectively the organization is achieving key business objectives.

---

## L

**Lazy Loading**
: Design pattern that defers initialization of objects until they are actually needed, used in ORM relationships.

---

## M

**Maintenance Préventive (Preventive Maintenance)**
: Scheduled maintenance performed to prevent equipment failures and extend equipment life.

**Migration**
: Process of moving from one database schema version to another, managed by Alembic.

**MIF Maroc**
: Organization name - presumably "Maintenance Industrielle France Maroc" or similar.

**Modèle (Model)**
: SQLAlchemy class that represents a database table and defines its structure and relationships.

---

## N

**Notification**
: System-generated message sent to users about important events, status changes, or required actions.

---

## O

**OpenAPI**
: Specification for describing REST APIs, formerly known as Swagger, providing interactive documentation.

**ORM (Object-Relational Mapping)**
: Programming technique that converts data between incompatible systems using object-oriented programming languages.

**Ouverte (Open)**
: Initial status of a newly created intervention that has not yet been assigned to a technician.

---

## P

**Planning**
: Scheduling information for interventions, including planned start and end times.

**PostgreSQL**
: Open-source relational database system used as the primary data store for the ERP system.

**Primary Key (PK)**
: Database constraint that uniquely identifies each row in a table.

**Priorité (Priority)**
: Classification of intervention urgency: urgente, haute, normale, basse, programmée.

**Pydantic**
: Data validation library for Python that uses type hints to validate, serialize, and deserialize data.

---

## Q

**Query Parameter**
: Part of a URL that assigns values to specified parameters, used for filtering and pagination.

---

## R

**RBAC (Role-Based Access Control)**
: Method of restricting system access to authorized users based on their assigned roles.

**ReDoc**
: Alternative documentation interface for OpenAPI specifications, providing a clean reference format.

**Responsable**
: Management role with oversight of operations, able to assign technicians and manage interventions.

**REST (Representational State Transfer)**
: Architectural style for designing networked applications, used for the API design.

---

## S

**Schema**
: Pydantic model that defines the structure and validation rules for API request and response data.

**Seeding**
: Process of populating the database with initial or test data.

**Session**
: Database connection context that manages transactions and object lifecycle.

**SQLAlchemy**
: Python SQL toolkit and ORM that provides application developers with the full power and flexibility of SQL.

**Statut (Status)**
: Current state of an intervention in the workflow (ouverte, affectée, en_cours, etc.).

**Swagger UI**
: Interactive documentation interface for OpenAPI specifications, allowing API testing from the browser.

---

## T

**Technicien (Technician)**
: Field service professional who performs maintenance interventions on equipment.

**Token**
: Authentication credential (JWT) that grants access to protected API endpoints.

---

## U

**Urgence (Urgency)**
: Boolean flag indicating whether an intervention requires immediate attention.

**User**
: Base entity for system authentication, extended by specific roles (technicien, client, etc.).

---

## V

**Validation**
: Process of ensuring that data meets specified requirements and business rules before processing.

**Versioning**
: Practice of managing changes to the API by maintaining multiple versions simultaneously.

---

## W

**Workflow**
: Sequence of steps that an intervention goes through from creation to completion.

---

## Business Domain Terms

### Maintenance Terminology

**Amélioration (Improvement)**
: Type of intervention focused on upgrading or enhancing equipment capabilities.

**Diagnostic**
: Type of intervention focused on analyzing and identifying equipment issues without necessarily performing repairs.

**Disponibilité (Availability)**
: Status indicating whether a technician is available for new intervention assignments.

**Durée Estimée (Estimated Duration)**
: Predicted time required to complete an intervention, measured in hours.

**Durée Réelle (Actual Duration)**
: Actual time taken to complete an intervention, measured in hours.

**Satisfaction Client (Client Satisfaction)**
: Rating scale (1-5) provided by clients to evaluate the quality of completed interventions.

### Equipment Classifications

**Critique (Critical)**
: Equipment classification indicating highest importance to operations, requiring immediate attention when issues arise.

**Normale (Normal)**
: Standard equipment classification for routine maintenance priority.

**Opérationnel (Operational)**
: Equipment status indicating normal functioning condition.

**Panne (Breakdown)**
: Equipment status indicating failure or malfunction requiring immediate intervention.

**Retiré (Retired)**
: Equipment status indicating permanent removal from service.

### Service Levels

**Platinum/Gold/Standard/Basic**
: Client service tier classifications determining response times and service quality levels.

**SLA (Service Level Agreement)**
: Contract terms defining expected service levels, response times, and quality standards.

---

## Technical Terminology

### Database Terms

**CASCADE**
: Referential action that automatically deletes related records when a parent record is deleted.

**Index**
: Database structure that improves query performance by providing fast access paths to data.

**Constraint**
: Rule enforced by the database to maintain data integrity and consistency.

**Relationship**
: Association between database tables, such as one-to-one, one-to-many, or many-to-many.

### API Terms

**Endpoint**
: Specific URL path that accepts API requests and returns responses.

**Middleware**
: Software that sits between applications and provides services like authentication, logging, or CORS handling.

**Pagination**
: Technique for dividing large datasets into smaller, manageable chunks for API responses.

**Rate Limiting**
: Practice of controlling the number of API requests a client can make within a specified time period.

### Security Terms

**Authentication**
: Process of verifying the identity of a user or system.

**Authorization**
: Process of determining what actions an authenticated user is allowed to perform.

**Encryption**
: Process of converting data into a coded format to prevent unauthorized access.

**Salt**
: Random data added to passwords before hashing to prevent rainbow table attacks.

---

## Acronyms and Abbreviations

| Acronym | Full Form | Context |
|---------|-----------|---------|
| **API** | Application Programming Interface | Web services |
| **CORS** | Cross-Origin Resource Sharing | Web security |
| **CRUD** | Create, Read, Update, Delete | Data operations |
| **ERP** | Enterprise Resource Planning | Business software |
| **FK** | Foreign Key | Database relationships |
| **HTTP** | HyperText Transfer Protocol | Web communication |
| **JSON** | JavaScript Object Notation | Data format |
| **JWT** | JSON Web Token | Authentication |
| **KPI** | Key Performance Indicator | Metrics |
| **ORM** | Object-Relational Mapping | Database abstraction |
| **PK** | Primary Key | Database unique identifier |
| **QA** | Quality Assurance | Testing and validation |
| **RBAC** | Role-Based Access Control | Security model |
| **REST** | Representational State Transfer | API architecture |
| **SLA** | Service Level Agreement | Contract terms |
| **SQL** | Structured Query Language | Database queries |
| **UI** | User Interface | Application presentation |
| **URL** | Uniform Resource Locator | Web addresses |

---

## Usage Guidelines

### For Developers
- Use consistent terminology in code comments and documentation
- Reference this glossary when creating new features or APIs
- Ensure new terms are added to maintain completeness

### For Business Users
- Refer to business domain terms when discussing requirements
- Use standardized terminology in user stories and specifications
- Maintain consistency in user interface labels and messages

### For Technical Writers
- Link to relevant glossary terms in documentation
- Keep definitions concise but complete
- Update glossary when new features are added

---

*This glossary serves as the definitive reference for terminology used throughout the ERP MIF Maroc system. It should be updated regularly as the system evolves and new concepts are introduced.*