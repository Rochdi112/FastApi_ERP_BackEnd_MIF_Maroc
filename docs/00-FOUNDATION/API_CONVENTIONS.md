---
title: "ERP MIF Maroc - API Design Conventions"
path: "docs/00-FOUNDATION/API_CONVENTIONS.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["api", "rest", "conventions", "design", "standards", "openapi"]
---

# ERP MIF Maroc - API Design Conventions

## API Design Overview

The ERP MIF Maroc API follows **RESTful design principles** with consistent patterns for resource naming, HTTP methods, status codes, and response formats. The API is designed for clarity, predictability, and ease of integration with frontend applications and external systems.

## Base API Structure

### URL Structure

**Base URL Pattern**
```
{scheme}://{host}:{port}/{api_version}/{resource}[/{resource_id}][/{sub_resource}]
```

**Examples**
```
http://localhost:8000/api/v1/interventions
http://localhost:8000/api/v1/interventions/123
http://localhost:8000/api/v1/interventions/123/documents
http://localhost:8000/api/v1/users/me
```

### API Versioning

**Current Version**: `v1`
- **Prefix**: `/api/v1`
- **Strategy**: URL-based versioning for clear API evolution
- **Backward Compatibility**: Legacy endpoints at root level for transition

**Version Strategy**
```mermaid
graph LR
    A[Frontend] --> B[/api/v1/users]
    A --> C[/api/v1/interventions]
    A --> D[/api/v1/equipements]
    
    E[Legacy Clients] --> F[/users]
    E --> G[/interventions]
    E --> H[/equipements]
    
    B --> I[Users Service]
    C --> J[Interventions Service]
    D --> K[Equipment Service]
    
    F --> I
    G --> J
    H --> K
```

## HTTP Methods & Resource Operations

### Standard CRUD Operations

| HTTP Method | Operation | Example | Description |
|-------------|-----------|---------|-------------|
| `GET` | Read | `GET /api/v1/users` | List all users |
| `GET` | Read | `GET /api/v1/users/123` | Get specific user |
| `POST` | Create | `POST /api/v1/users` | Create new user |
| `PUT` | Update | `PUT /api/v1/users/123` | Full update of user |
| `PATCH` | Partial Update | `PATCH /api/v1/users/123` | Partial update of user |
| `DELETE` | Delete | `DELETE /api/v1/users/123` | Delete user |

### Resource-Specific Patterns

**Collection Operations**
```http
GET    /api/v1/interventions           # List interventions
POST   /api/v1/interventions           # Create intervention
```

**Individual Resource Operations**
```http
GET    /api/v1/interventions/123       # Get intervention
PUT    /api/v1/interventions/123       # Update intervention
PATCH  /api/v1/interventions/123       # Partial update
DELETE /api/v1/interventions/123       # Delete intervention
```

**Sub-resource Operations**
```http
GET    /api/v1/interventions/123/documents    # Get intervention documents
POST   /api/v1/interventions/123/documents    # Add document to intervention
```

**Action-based Operations**
```http
PATCH  /api/v1/interventions/123/status       # Change intervention status
POST   /api/v1/interventions/123/assign       # Assign technician
```

## Request/Response Formats

### Content Types

**Request Content Types**
- `application/json` - Standard API requests
- `application/x-www-form-urlencoded` - Authentication endpoints
- `multipart/form-data` - File uploads

**Response Content Types**
- `application/json` - All API responses
- `application/pdf` - Generated reports
- `text/csv` - Data exports

### Request Format Standards

**JSON Request Example**
```json
{
  "equipement_id": 123,
  "type_intervention": "corrective",
  "priorite": "haute",
  "urgence": true,
  "titre": "Panne pompe principale",
  "description": "La pompe principale présente des dysfonctionnements..."
}
```

**Request Validation Rules**
- All fields follow `snake_case` naming convention
- Required fields clearly documented in OpenAPI schema
- Enum values use lowercase with underscores
- Dates use ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`)
- Numbers use appropriate precision (integers, decimals)

### Response Format Standards

**Successful Response Format**
```json
{
  "id": 123,
  "equipement_id": 456,
  "type_intervention": "corrective",
  "statut": "ouverte",
  "priorite": "haute",
  "urgence": true,
  "titre": "Panne pompe principale",
  "description": "La pompe principale présente des dysfonctionnements...",
  "date_creation": "2025-01-27T10:00:00Z",
  "date_planifiee": null,
  "technicien_id": null,
  "client_id": 789
}
```

**Error Response Format**
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "equipement_id",
      "message": "Field required",
      "type": "missing"
    },
    {
      "field": "priorite",
      "message": "Invalid enum value",
      "type": "value_error"
    }
  ]
}
```

## HTTP Status Codes

### Standard Status Code Usage

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| **2xx Success** | | |
| `200 OK` | Success | GET, PUT, PATCH operations |
| `201 Created` | Resource created | POST operations |
| `204 No Content` | Success, no content | DELETE operations |
| **4xx Client Error** | | |
| `400 Bad Request` | Invalid request data | Validation errors |
| `401 Unauthorized` | Authentication required | Missing/invalid token |
| `403 Forbidden` | Access denied | Insufficient permissions |
| `404 Not Found` | Resource not found | Non-existent resource |
| `409 Conflict` | Resource conflict | Duplicate creation |
| `422 Unprocessable Entity` | Validation failed | Business rule violations |
| **5xx Server Error** | | |
| `500 Internal Server Error` | Server error | Unexpected server issues |
| `502 Bad Gateway` | External service error | Database/service unavailable |
| `503 Service Unavailable` | Service temporary unavailable | Maintenance mode |

### Status Code Examples

**Successful Operations**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "username": "johndoe",
  "email": "john@example.com"
}
```

**Resource Creation**
```http
HTTP/1.1 201 Created
Location: /api/v1/interventions/456
Content-Type: application/json

{
  "id": 456,
  "titre": "Nouvelle intervention",
  "statut": "ouverte"
}
```

**Validation Error**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "detail": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

**Authentication Error**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Authentication required"
}
```

**Authorization Error**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "detail": "Accès refusé. Rôles autorisés: admin, responsable"
}
```

## Authentication & Authorization

### Authentication Header

**Bearer Token Format**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Request**
```http
GET /api/v1/users/me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Authentication Endpoints

**Login Endpoint**
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=secretpassword
```

**Response**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Query Parameters & Filtering

### Pagination Parameters

**Standard Pagination**
```http
GET /api/v1/interventions?limit=10&offset=20
```

**Parameters**
- `limit` (integer): Number of results per page (default: 50, max: 100)
- `offset` (integer): Number of results to skip (default: 0)

**Pagination Response**
```json
{
  "data": [...],
  "pagination": {
    "limit": 10,
    "offset": 20,
    "total": 150,
    "has_next": true,
    "has_prev": true
  }
}
```

### Filtering Parameters

**Common Filter Patterns**
```http
GET /api/v1/interventions?statut=ouverte&urgence=true&technicien_id=123
GET /api/v1/equipements?client_id=456&statut=operationnel
GET /api/v1/users?role=technicien&is_active=true
```

**Date Range Filtering**
```http
GET /api/v1/interventions?date_debut_gte=2025-01-01&date_debut_lte=2025-01-31
```

**Search Parameters**
```http
GET /api/v1/interventions?search=pompe
GET /api/v1/clients?search=ACME
```

### Sorting Parameters

**Sort Syntax**
```http
GET /api/v1/interventions?sort=date_creation    # Ascending
GET /api/v1/interventions?sort=-date_creation   # Descending
GET /api/v1/interventions?sort=priorite,-date_creation  # Multiple fields
```

**Available Sort Fields**
- Most endpoints support sorting by primary fields
- Date fields typically support chronological sorting
- Enum fields support sorting by enum order

## Response Schemas

### Standard Response Patterns

**Single Resource Response**
```json
{
  "id": 123,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

**Collection Response**
```json
{
  "data": [
    {
      "id": 123,
      "field1": "value1"
    },
    {
      "id": 124,
      "field1": "value2"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 2,
    "has_next": false,
    "has_prev": false
  }
}
```

**Error Response**
```json
{
  "detail": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### Field Naming Conventions

**Naming Rules**
- Use `snake_case` for all field names
- Use descriptive, clear names
- Avoid abbreviations unless widely understood
- Use consistent naming across resources

**Common Field Patterns**
```json
{
  "id": 123,                           // Primary key
  "parent_id": 456,                    // Foreign key reference
  "is_active": true,                   // Boolean flags
  "created_at": "2025-01-27T10:00:00Z", // Timestamps
  "updated_at": "2025-01-27T10:00:00Z",
  "date_debut": "2025-01-27",          // Dates without time
  "type_intervention": "corrective",    // Enum values
  "nom_entreprise": "ACME Corp",       // Descriptive strings
  "notes_techniques": "Long text..."    // Text fields
}
```

## OpenAPI Documentation

### OpenAPI Schema Standards

**Endpoint Documentation**
```python
@router.post(
    "/",
    response_model=InterventionOut,
    status_code=201,
    summary="Créer une nouvelle intervention",
    description="Crée une nouvelle intervention de maintenance avec les détails fournis.",
    responses={
        201: {"description": "Intervention créée avec succès"},
        400: {"description": "Données invalides"},
        401: {"description": "Authentification requise"},
        403: {"description": "Permissions insuffisantes"}
    }
)
def create_intervention(
    intervention: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth_required)
):
    """Detailed endpoint implementation."""
    pass
```

**Schema Documentation**
```python
class InterventionCreate(BaseModel):
    equipement_id: int = Field(..., description="ID de l'équipement concerné")
    type_intervention: InterventionType = Field(..., description="Type d'intervention")
    priorite: PrioriteIntervention = Field(default=PrioriteIntervention.normale)
    urgence: bool = Field(default=False, description="Intervention urgente")
    titre: str = Field(..., min_length=5, max_length=255, description="Titre de l'intervention")
    description: str = Field(..., min_length=10, max_length=2000, description="Description détaillée")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "equipement_id": 123,
                "type_intervention": "corrective",
                "priorite": "haute",
                "urgence": true,
                "titre": "Réparation pompe principale",
                "description": "La pompe principale présente des dysfonctionnements nécessitant une intervention immédiate."
            }
        }
    )
```

### Documentation Access

**Interactive Documentation**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Resource Endpoint Patterns

### Users Resource

```http
# User management
GET    /api/v1/users                   # List users (admin/responsable)
POST   /api/v1/users                   # Create user (admin)
GET    /api/v1/users/me                # Get current user profile
PUT    /api/v1/users/update            # Update current user profile
GET    /api/v1/users/{user_id}         # Get specific user
DELETE /api/v1/users/{user_id}         # Delete user (admin)
PATCH  /api/v1/users/{user_id}/activate # Activate/deactivate user (admin)
```

### Interventions Resource

```http
# Intervention management
GET    /api/v1/interventions           # List interventions
POST   /api/v1/interventions           # Create intervention
GET    /api/v1/interventions/{id}      # Get intervention details
PUT    /api/v1/interventions/{id}      # Update intervention
PATCH  /api/v1/interventions/{id}/status # Update intervention status
DELETE /api/v1/interventions/{id}      # Delete intervention

# Sub-resources
GET    /api/v1/interventions/{id}/documents # Get intervention documents
POST   /api/v1/interventions/{id}/documents # Add document
GET    /api/v1/interventions/{id}/history   # Get intervention history
```

### Equipment Resource

```http
# Equipment management
GET    /api/v1/equipements             # List equipment
POST   /api/v1/equipements             # Create equipment
GET    /api/v1/equipements/{id}        # Get equipment details
PUT    /api/v1/equipements/{id}        # Update equipment
DELETE /api/v1/equipements/{id}        # Delete equipment

# Equipment-specific actions
PATCH  /api/v1/equipements/{id}/status # Update equipment status
GET    /api/v1/equipements/{id}/interventions # Get equipment interventions
```

## Error Handling Patterns

### Validation Errors

**Field Validation Error**
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    },
    {
      "field": "age",
      "message": "Value must be greater than 0",
      "type": "value_error.number.not_gt",
      "context": {"limit_value": 0}
    }
  ]
}
```

**Business Rule Violation**
```json
{
  "detail": "Business rule violation",
  "code": "TECHNICIAN_ALREADY_ASSIGNED",
  "message": "Le technicien est déjà assigné à une autre intervention",
  "context": {
    "technician_id": 123,
    "existing_intervention_id": 456
  }
}
```

### Database Errors

**Resource Not Found**
```json
{
  "detail": "Intervention not found",
  "code": "RESOURCE_NOT_FOUND",
  "resource_type": "intervention",
  "resource_id": 123
}
```

**Duplicate Resource**
```json
{
  "detail": "Email already exists",
  "code": "DUPLICATE_RESOURCE",
  "field": "email",
  "value": "user@example.com"
}
```

## File Upload Conventions

### Upload Endpoints

**Document Upload**
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="rapport.pdf"
Content-Type: application/pdf

[file content]
--boundary
Content-Disposition: form-data; name="intervention_id"

123
--boundary--
```

**Upload Response**
```json
{
  "id": 789,
  "nom_fichier": "rapport.pdf",
  "chemin": "/static/uploads/interventions/123/rapport_20250127_100000.pdf",
  "type_document": "rapport",
  "taille": 2048576,
  "url": "/static/uploads/interventions/123/rapport_20250127_100000.pdf",
  "date_upload": "2025-01-27T10:00:00Z"
}
```

### File Access

**Static File URLs**
```http
GET /static/uploads/interventions/123/rapport_20250127_100000.pdf
```

**File Download Headers**
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="rapport.pdf"
Content-Length: 2048576
```

## Rate Limiting & Throttling

### Rate Limit Headers

**Rate Limit Information**
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

**Rate Limit Exceeded**
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 60

{
  "detail": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## API Versioning Strategy

### Version Management

**Current Version (v1)**
- All new endpoints under `/api/v1`
- Stable API contract
- Backward compatibility maintained

**Legacy Support**
- Root-level endpoints maintained for transition
- Gradual migration to versioned endpoints
- Deprecation notices in headers

**Future Versions**
- Breaking changes require new version (v2)
- Parallel version support during transition
- Clear migration documentation

### Version Headers

**API Version Information**
```http
HTTP/1.1 200 OK
API-Version: v1
API-Deprecated: false
API-Sunset: 2026-12-31T23:59:59Z
```

## Testing API Conventions

### Test Data Standards

**Consistent Test Data**
```json
{
  "test_user": {
    "email": "test@example.com",
    "username": "testuser",
    "role": "technicien"
  },
  "test_intervention": {
    "titre": "Test intervention",
    "type_intervention": "corrective",
    "priorite": "normale"
  }
}
```

### API Contract Testing

**Contract Validation**
- OpenAPI schema compliance
- Request/response format validation
- HTTP status code verification
- Error response format testing

---

*This API conventions documentation establishes consistent patterns and standards for the ERP MIF Maroc API design. These conventions ensure predictable behavior and ease of integration for frontend and external systems.*