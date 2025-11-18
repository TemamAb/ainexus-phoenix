#!/usr/bin/env python3
"""
AI-NEXUS API Documentation Generator
Automated OpenAPI/Swagger documentation
"""

import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class APIEndpoint:
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict]
    responses: Dict
    tags: List[str]

class APIDocumentationGenerator:
    """Generate comprehensive API documentation"""
    
    def __init__(self):
        self.endpoints = []
        self.schemas = {}
        
    def add_endpoint(self, endpoint: APIEndpoint):
        """Add API endpoint to documentation"""
        self.endpoints.append(endpoint)
    
    def generate_openapi_spec(self) -> Dict:
        """Generate OpenAPI 3.0 specification"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "AI-NEXUS Arbitrage System API",
                "description": "Enterprise-grade DeFi arbitrage trading system with AI-powered execution",
                "version": "5.0.0",
                "contact": {
                    "name": "AI-NEXUS Enterprise Support",
                    "email": "enterprise@ainexus.com",
                    "url": "https://ainexus.com"
                },
                "license": {
                    "name": "Proprietary",
                    "url": "https://ainexus.com/license"
                }
            },
            "servers": [
                {
                    "url": "https://api.ainexus.com/v1",
                    "description": "Production API server"
                },
                {
                    "url": "https://sandbox.ainexus.com/v1",
                    "description": "Sandbox API server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": self.schemas,
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    },
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            },
            "security": [
                {"BearerAuth": []},
                {"ApiKeyAuth": []}
            ]
        }
        
        # Add endpoints to paths
        for endpoint in self.endpoints:
            if endpoint.path not in openapi_spec["paths"]:
                openapi_spec["paths"][endpoint.path] = {}
            
            openapi_spec["paths"][endpoint.path][endpoint.method.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": endpoint.parameters,
                "responses": endpoint.responses,
                "security": [
                    {"BearerAuth": []},
                    {"ApiKeyAuth": []}
                ]
            }
        
        return openapi_spec
    
    def generate_markdown_docs(self) -> str:
        """Generate Markdown API documentation"""
        docs = "# AI-NEXUS API Documentation\n\n"
        docs += "## Overview\n\n"
        docs += "The AI-NEXUS API provides programmatic access to the enterprise-grade arbitrage trading system.\n\n"
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in self.endpoints:
            for tag in endpoint.tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Generate documentation for each tag
        for tag, tag_endpoints in endpoints_by_tag.items():
            docs += f"## {tag.title()}\n\n"
            
            for endpoint in tag_endpoints:
                docs += f"### {endpoint.method.upper()} {endpoint.path}\n\n"
                docs += f"**Summary**: {endpoint.summary}\n\n"
                docs += f"**Description**: {endpoint.description}\n\n"
                
                if endpoint.parameters:
                    docs += "**Parameters**:\n\n"
                    docs += "| Name | Type | Required | Description |\n"
                    docs += "|------|------|----------|-------------|\n"
                    for param in endpoint.parameters:
                        required = "Yes" if param.get('required', False) else "No"
                        docs += f"| {param['name']} | {param['schema']['type']} | {required} | {param.get('description', '')} |\n"
                    docs += "\n"
                
                if endpoint.responses:
                    docs += "**Responses**:\n\n"
                    for status_code, response in endpoint.responses.items():
                        docs += f"- **{status_code}**: {response.get('description', '')}\n"
                    docs += "\n"
        
        return docs
    
    def generate_postman_collection(self) -> Dict:
        """Generate Postman collection"""
        collection = {
            "info": {
                "name": "AI-NEXUS API",
                "description": "Enterprise arbitrage trading system API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for endpoint in self.endpoints:
            for tag in endpoint.tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Create Postman collection structure
        for tag, tag_endpoints in endpoints_by_tag.items():
            folder = {
                "name": tag.title(),
                "item": []
            }
            
            for endpoint in tag_endpoints:
                request = {
                    "name": endpoint.summary,
                    "request": {
                        "method": endpoint.method.upper(),
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            },
                            {
                                "key": "Authorization",
                                "value": "Bearer {{api_token}}"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + endpoint.path,
                            "host": ["{{base_url}}"],
                            "path": endpoint.path.strip('/').split('/')
                        }
                    },
                    "response": []
                }
                
                # Add parameters
                if endpoint.parameters:
                    if endpoint.method.lower() in ['get', 'delete']:
                        request["request"]["url"]["query"] = []
                        for param in endpoint.parameters:
                            if param['in'] == 'query':
                                request["request"]["url"]["query"].append({
                                    "key": param['name'],
                                    "value": f"{{{param['name']}}}"
                                })
                    else:
                        request["request"]["body"] = {
                            "mode": "raw",
                            "raw": "{}",
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                
                folder["item"].append(request)
            
            collection["item"].append(folder)
        
        return collection

# Predefined API endpoints for AI-NEXUS
def create_ainexus_endpoints():
    """Create AI-NEXUS API endpoints documentation"""
    generator = APIDocumentationGenerator()
    
    # System endpoints
    generator.add_endpoint(APIEndpoint(
        path="/health",
        method="GET",
        summary="System Health Check",
        description="Comprehensive health check of all system components",
        parameters=[],
        responses={
            "200": {
                "description": "System is healthy",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "timestamp": {"type": "string"},
                                "components": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        tags=["system", "monitoring"]
    ))
    
    # Arbitrage endpoints
    generator.add_endpoint(APIEndpoint(
        path="/arbitrage/opportunities",
        method="GET",
        summary="Get Arbitrage Opportunities",
        description="Retrieve current arbitrage opportunities across all monitored venues",
        parameters=[
            {
                "name": "min_profitability",
                "in": "query",
                "description": "Minimum profitability threshold",
                "required": False,
                "schema": {"type": "number", "minimum": 0}
            }
        ],
        responses={
            "200": {
                "description": "List of arbitrage opportunities",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "opportunities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "pair": {"type": "string"},
                                            "profitability": {"type": "number"},
                                            "estimated_profit": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        tags=["arbitrage", "trading"]
    ))
    
    # Strategy endpoints
    generator.add_endpoint(APIEndpoint(
        path="/strategies/{strategy_id}/enable",
        method="POST",
        summary="Enable Trading Strategy",
        description="Enable a specific arbitrage strategy",
        parameters=[
            {
                "name": "strategy_id",
                "in": "path",
                "description": "Strategy identifier",
                "required": True,
                "schema": {"type": "string"}
            }
        ],
        responses={
            "200": {
                "description": "Strategy enabled successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "strategy_id": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        tags=["strategies", "trading"]
    ))
    
    # Risk management endpoints
    generator.add_endpoint(APIEndpoint(
        path="/risk/limits",
        method="GET",
        summary="Get Risk Limits",
        description="Retrieve current risk management limits and settings",
        parameters=[],
        responses={
            "200": {
                "description": "Risk limits configuration",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "daily_loss_limit": {"type": "number"},
                                "max_position_size": {"type": "number"},
                                "var_confidence": {"type": "number"}
                            }
                        }
                    }
                }
            }
        },
        tags=["risk", "management"]
    ))
    
    # Performance endpoints
    generator.add_endpoint(APIEndpoint(
        path="/performance/metrics",
        method="GET",
        summary="Get Performance Metrics",
        description="Retrieve system performance and trading metrics",
        parameters=[],
        responses={
            "200": {
                "description": "Performance metrics",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "total_executions": {"type": "integer"},
                                "success_rate": {"type": "number"},
                                "total_profit": {"type": "number"}
                            }
                        }
                    }
                }
            }
        },
        tags=["performance", "analytics"]
    ))
    
    return generator

# Generate all documentation formats
if __name__ == "__main__":
    generator = create_ainexus_endpoints()
    
    # Generate OpenAPI specification
    openapi_spec = generator.generate_openapi_spec()
    with open('documentation/openapi.json', 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    
    # Generate Markdown documentation
    markdown_docs = generator.generate_markdown_docs()
    with open('documentation/API.md', 'w') as f:
        f.write(markdown_docs)
    
    # Generate Postman collection
    postman_collection = generator.generate_postman_collection()
    with open('documentation/postman_collection.json', 'w') as f:
        json.dump(postman_collection, f, indent=2)
    
    print("API documentation generated successfully!")
    print("- OpenAPI spec: documentation/openapi.json")
    print("- Markdown docs: documentation/API.md")
    print("- Postman collection: documentation/postman_collection.json")
