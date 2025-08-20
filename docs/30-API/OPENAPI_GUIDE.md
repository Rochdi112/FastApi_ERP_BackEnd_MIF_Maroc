---
title: "ERP MIF Maroc - OpenAPI Usage Guide"
path: "docs/30-API/OPENAPI_GUIDE.md"
owner: "backend-team"
version: "0.1"
updated: "2025-01-27"
tags: ["openapi", "swagger", "api-documentation", "integration"]
---

# ERP MIF Maroc - OpenAPI Usage Guide

## OpenAPI Overview

The ERP MIF Maroc API provides comprehensive OpenAPI (Swagger) documentation for all endpoints, schemas, and authentication methods. This guide explains how to use the OpenAPI documentation effectively for development, testing, and integration.

## Accessing API Documentation

### Available Documentation Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Swagger UI** | `http://localhost:8000/docs` | Interactive API exploration and testing |
| **ReDoc** | `http://localhost:8000/redoc` | Clean, comprehensive API reference |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` | Machine-readable OpenAPI specification |
| **Generated JSON** | `openapi.generated.json` | Exported specification file |

### Development vs Production URLs

**Development Environment**
```
Base URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

**Production Environment**
```
Base URL: https://api.erp-mif-maroc.com
Swagger UI: https://api.erp-mif-maroc.com/docs
ReDoc: https://api.erp-mif-maroc.com/redoc
```

## OpenAPI Specification Structure

### API Information

```json
{
  "openapi": "3.0.3",
  "info": {
    "title": "ERP Interventions",
    "version": "1.0.0",
    "description": "Backend ERP pour la gestion des interventions industrielles",
    "contact": {
      "name": "Backend Team",
      "email": "backend-team@mif-maroc.com"
    },
    "license": {
      "name": "Proprietary"
    }
  },
  "servers": [
    {
      "url": "/api/v1",
      "description": "API Version 1"
    }
  ]
}
```

### Security Schemes

**JWT Bearer Authentication**
```json
{
  "securitySchemes": {
    "BearerAuth": {
      "type": "http",
      "scheme": "bearer",
      "bearerFormat": "JWT",
      "description": "JWT token obtained from /auth/token endpoint"
    }
  },
  "security": [
    {
      "BearerAuth": []
    }
  ]
}
```

## Tag Organization

### Service Tags Mapping

The API endpoints are organized by business domain tags:

| Tag | Service Domain | Description |
|-----|----------------|-------------|
| `auth` | Authentication | JWT token management and user authentication |
| `users` | User Management | User accounts and profile management |
| `techniciens` | Technician Management | Technician profiles and competencies |
| `clients` | Client Management | Client organizations and relationships |
| `equipements` | Equipment Management | Equipment inventory and status tracking |
| `interventions` | Intervention Management | Core maintenance workflow management |
| `planning` | Planning & Scheduling | Intervention scheduling and calendar |
| `notifications` | Communication | Real-time notifications and messaging |
| `documents` | Document Management | File uploads and document handling |
| `filtres` | Search & Filtering | Advanced filtering and search capabilities |

### Tag Structure Example

```json
{
  "tags": [
    {
      "name": "auth",
      "description": "Authentication endpoints for JWT token management"
    },
    {
      "name": "interventions",
      "description": "Core business logic for maintenance intervention management"
    },
    {
      "name": "equipements",
      "description": "Equipment inventory and asset management"
    }
  ]
}
```

## Schema Definitions

### Model Schemas

**Request/Response Schema Pattern**
```json
{
  "components": {
    "schemas": {
      "InterventionCreate": {
        "type": "object",
        "required": ["equipement_id", "titre", "description", "type_intervention"],
        "properties": {
          "equipement_id": {
            "type": "integer",
            "description": "ID de l'équipement concerné"
          },
          "titre": {
            "type": "string",
            "minLength": 5,
            "maxLength": 255,
            "description": "Titre de l'intervention"
          },
          "description": {
            "type": "string",
            "minLength": 10,
            "maxLength": 2000,
            "description": "Description détaillée"
          },
          "type_intervention": {
            "$ref": "#/components/schemas/InterventionType"
          },
          "priorite": {
            "$ref": "#/components/schemas/PrioriteIntervention",
            "default": "normale"
          },
          "urgence": {
            "type": "boolean",
            "default": false,
            "description": "Intervention urgente"
          }
        },
        "example": {
          "equipement_id": 123,
          "titre": "Réparation pompe principale",
          "description": "La pompe principale présente des dysfonctionnements nécessitant une intervention immédiate.",
          "type_intervention": "corrective",
          "priorite": "haute",
          "urgence": true
        }
      },
      "InterventionOut": {
        "type": "object",
        "properties": {
          "id": {
            "type": "integer",
            "description": "Identifiant unique"
          },
          "equipement_id": {
            "type": "integer"
          },
          "technicien_id": {
            "type": "integer",
            "nullable": true
          },
          "client_id": {
            "type": "integer"
          },
          "statut": {
            "$ref": "#/components/schemas/StatutIntervention"
          },
          "date_creation": {
            "type": "string",
            "format": "date-time"
          },
          "date_planifiee": {
            "type": "string",
            "format": "date-time",
            "nullable": true
          }
        }
      }
    }
  }
}
```

### Enum Schemas

**Business Enums Documentation**
```json
{
  "InterventionType": {
    "type": "string",
    "enum": ["corrective", "preventive", "ameliorative", "diagnostic"],
    "description": "Type d'intervention de maintenance",
    "example": "corrective"
  },
  "StatutIntervention": {
    "type": "string",
    "enum": ["ouverte", "affectee", "en_cours", "en_attente", "cloturee", "annulee", "archivee"],
    "description": "Statut dans le workflow d'intervention",
    "example": "ouverte"
  },
  "PrioriteIntervention": {
    "type": "string",
    "enum": ["urgente", "haute", "normale", "basse", "programmee"],
    "description": "Niveau de priorité de l'intervention",
    "example": "normale"
  }
}
```

## Endpoint Documentation

### Endpoint Structure

**Standard Endpoint Documentation**
```json
{
  "paths": {
    "/interventions/": {
      "post": {
        "tags": ["interventions"],
        "summary": "Créer une nouvelle intervention",
        "description": "Crée une nouvelle intervention de maintenance avec les détails fournis.",
        "operationId": "create_intervention",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/InterventionCreate"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Intervention créée avec succès",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/InterventionOut"
                }
              }
            }
          },
          "400": {
            "description": "Données invalides",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ValidationError"
                }
              }
            }
          },
          "401": {
            "description": "Authentification requise"
          },
          "403": {
            "description": "Permissions insuffisantes"
          }
        },
        "security": [
          {
            "BearerAuth": []
          }
        ]
      }
    }
  }
}
```

### Response Examples

**Success Response Example**
```json
{
  "responses": {
    "200": {
      "description": "Operation successful",
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/InterventionOut"
          },
          "examples": {
            "corrective_intervention": {
              "summary": "Corrective intervention example",
              "value": {
                "id": 123,
                "equipement_id": 456,
                "technicien_id": 789,
                "client_id": 101,
                "type_intervention": "corrective",
                "statut": "affectee",
                "priorite": "haute",
                "urgence": true,
                "titre": "Réparation pompe principale",
                "description": "Intervention urgente sur la pompe principale",
                "date_creation": "2025-01-27T10:00:00Z",
                "date_planifiee": "2025-01-27T14:00:00Z"
              }
            }
          }
        }
      }
    }
  }
}
```

## Using Swagger UI

### Interactive API Testing

**Authentication Setup**
1. Click the "Authorize" button in Swagger UI
2. Enter your JWT token in the format: `Bearer <your-token>`
3. Click "Authorize" to apply to all requests

**Testing Endpoints**
1. Navigate to the desired endpoint
2. Click "Try it out"
3. Fill in required parameters
4. Click "Execute"
5. Review response in the "Response" section

### Example Authentication Flow

```bash
# Step 1: Get JWT token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=admin@example.com&password=admin123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# Step 2: Use token in Swagger UI authorization
# Enter in authorization dialog: Bearer eyJ...

# Step 3: Test protected endpoints through Swagger UI
```

## Code Generation

### Client SDK Generation

**Using OpenAPI Generator**
```bash
# Install OpenAPI Generator
npm install @openapitools/openapi-generator-cli -g

# Generate TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./generated-client \
  --additional-properties=withSeparateModelsAndApi=true

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client \
  --additional-properties=packageName=erp_api_client
```

**Generated Client Usage Example**
```typescript
// TypeScript client usage
import { Configuration, InterventionsApi } from './generated-client';

const config = new Configuration({
  basePath: 'http://localhost:8000/api/v1',
  accessToken: 'eyJ...' // Your JWT token
});

const interventionsApi = new InterventionsApi(config);

// Create intervention
const newIntervention = await interventionsApi.createNewIntervention({
  equipement_id: 123,
  titre: "Test Intervention",
  description: "Test description",
  type_intervention: "corrective"
});
```

### Postman Collection Generation

**Import OpenAPI to Postman**
1. Open Postman
2. Click "Import" button
3. Select "Link" tab
4. Enter: `http://localhost:8000/openapi.json`
5. Configure authentication in collection settings

**Postman Environment Variables**
```json
{
  "name": "ERP MIF Maroc - Development",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api/v1"
    },
    {
      "key": "auth_token",
      "value": "{{jwt_token}}"
    }
  ]
}
```

## OpenAPI Generation Process

### Automatic Generation

**FastAPI Auto-Generation**
- OpenAPI specification automatically generated from:
  - Route definitions and decorators
  - Pydantic schema models
  - Type hints and annotations
  - Docstrings and descriptions
  - Response model specifications

**Generation Configuration**
```python
# app/main.py
app = FastAPI(
    title="ERP Interventions",
    version="1.0.0",
    description="Backend ERP pour la gestion des interventions industrielles",
    openapi_url="/openapi.json",  # OpenAPI JSON endpoint
    docs_url="/docs",             # Swagger UI
    redoc_url="/redoc"            # ReDoc interface
)
```

### Manual Export

**Export OpenAPI Specification**
```bash
# Export current OpenAPI spec
curl http://localhost:8000/openapi.json > openapi.json

# Using the export script
python scripts/openapi_export.py > openapi.generated.json

# Validate OpenAPI spec
npx swagger-codegen-cli validate -i openapi.json
```

### Custom OpenAPI Customization

**Enhanced Metadata**
```python
# Custom OpenAPI schema modification
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ERP MIF Maroc API",
        version="1.0.0",
        description="Comprehensive ERP system for industrial maintenance management",
        routes=app.routes,
    )
    
    # Add custom metadata
    openapi_schema["info"]["contact"] = {
        "name": "Backend Team",
        "email": "backend-team@mif-maroc.com"
    }
    
    # Add server information
    openapi_schema["servers"] = [
        {"url": "/api/v1", "description": "Production API"},
        {"url": "http://localhost:8000/api/v1", "description": "Development API"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Integration Examples

### Frontend Integration

**React/TypeScript Integration**
```typescript
// API client setup
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add authentication interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Use OpenAPI-generated types
interface Intervention {
  id: number;
  titre: string;
  statut: 'ouverte' | 'affectee' | 'en_cours' | 'cloturee';
  // ... other fields from OpenAPI schema
}

// API service functions
export const interventionsService = {
  async getInterventions(): Promise<Intervention[]> {
    const response = await apiClient.get('/interventions/');
    return response.data;
  },
  
  async createIntervention(data: InterventionCreate): Promise<Intervention> {
    const response = await apiClient.post('/interventions/', data);
    return response.data;
  }
};
```

### Backend-to-Backend Integration

**Python Service Integration**
```python
# Using requests with OpenAPI schema validation
import requests
from typing import Dict, List
import json

class ERPApiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
    
    def get_interventions(self, **filters) -> List[Dict]:
        """Get interventions with optional filtering."""
        response = self.session.get(
            f"{self.base_url}/interventions/",
            params=filters
        )
        response.raise_for_status()
        return response.json()
    
    def create_intervention(self, intervention_data: Dict) -> Dict:
        """Create new intervention."""
        response = self.session.post(
            f"{self.base_url}/interventions/",
            json=intervention_data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = ERPApiClient("http://localhost:8000/api/v1", "your-jwt-token")
interventions = client.get_interventions(statut="ouverte")
```

## Documentation Maintenance

### Keeping Documentation Current

**Automated Updates**
- OpenAPI spec automatically reflects code changes
- Schema updates happen when Pydantic models change
- New endpoints appear automatically when routes are added

**Manual Review Process**
1. Review generated OpenAPI spec after significant changes
2. Update examples and descriptions as needed
3. Validate schema accuracy with real API responses
4. Update client SDKs when major changes occur

### Version Management

**API Versioning Strategy**
```python
# Multiple API versions support
app_v1 = FastAPI(
    title="ERP API v1",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)

app_v2 = FastAPI(
    title="ERP API v2", 
    version="2.0.0",
    openapi_url="/api/v2/openapi.json",
    docs_url="/api/v2/docs"
)

# Mount different versions
app.mount("/api/v1", app_v1)
app.mount("/api/v2", app_v2)
```

## Troubleshooting

### Common Issues

**Schema Generation Issues**
```python
# Issue: Missing schema for custom types
# Solution: Ensure proper Pydantic model definition
class CustomResponse(BaseModel):
    status: str
    data: Optional[Dict] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {"key": "value"}
            }
        }
```

**Authentication Issues in Swagger UI**
```javascript
// Issue: CORS issues with authentication
// Solution: Ensure proper CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Validation Tools

**OpenAPI Specification Validation**
```bash
# Validate OpenAPI spec
npm install -g swagger-codegen-cli
swagger-codegen-cli validate -i http://localhost:8000/openapi.json

# Check for breaking changes
npm install -g oasdiff
oasdiff breaking openapi-old.json openapi-new.json
```

---

*This OpenAPI guide provides comprehensive information for effectively using, generating, and integrating with the ERP MIF Maroc API documentation and specifications.*