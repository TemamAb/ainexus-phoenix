"""
Kubernetes Orchestrator for Trading System Deployment

This module provides comprehensive Kubernetes orchestration capabilities
for deploying, scaling, and managing the quantitative trading system
in containerized environments.

Key Features:
- Multi-cluster deployment management
- Automated scaling based on market conditions
- Service discovery and load balancing
- Rolling updates and canary deployments
- Resource optimization and cost management
"""

import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import tempfile
import os
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    """Kubernetes deployment strategies"""
    ROLLING_UPDATE = "rolling_update"
    RECREATE = "recreate"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"

class ResourceType(Enum):
    """Kubernetes resource types"""
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    INGRESS = "ingress"
    PERSISTENT_VOLUME_CLAIM = "pvc"
    HORIZONTAL_POD_AUTOSCALER = "hpa"

class ClusterEnvironment(Enum):
    """Cluster environment types"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"

@dataclass
class ResourceRequirements:
    """Kubernetes resource requirements"""
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "128Mi"
    memory_limit: str = "512Mi"
    storage_request: str = "1Gi"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    name: str
    image: str
    replicas: int
    strategy: DeploymentStrategy
    resource_requirements: ResourceRequirements
    environment_vars: Dict[str, str]
    labels: Dict[str, str]
    annotations: Dict[str, str]

@dataclass
class ClusterConfig:
    """Kubernetes cluster configuration"""
    cluster_name: str
    environment: ClusterEnvironment
    context: str
    namespace: str
    api_server: str
    version: str

@dataclass
class ScalingConfig:
    """Auto-scaling configuration"""
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: int
    target_memory_utilization: int
    custom_metrics: List[Dict[str, Any]]

class KubernetesOrchestrator:
    """
    Advanced Kubernetes orchestration engine for trading system deployment
    
    This class provides comprehensive Kubernetes management capabilities:
    - Multi-cluster deployment and management
    - Automated scaling based on trading load
    - Rolling updates with health checks
    - Resource optimization and monitoring
    - Disaster recovery and failover
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None, default_namespace: str = "trading"):
        """
        Initialize Kubernetes Orchestrator
        
        Args:
            kubeconfig_path: Path to kubeconfig file
            default_namespace: Default Kubernetes namespace
        """
        self.kubeconfig_path = kubeconfig_path
        self.default_namespace = default_namespace
        self.clusters: Dict[str, ClusterConfig] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        self._initialize_clusters()
        
    def _initialize_clusters(self):
        """Initialize cluster configurations"""
        # Production cluster
        self.clusters["production"] = ClusterConfig(
            cluster_name="trading-prod",
            environment=ClusterEnvironment.PRODUCTION,
            context="trading-prod",
            namespace="trading-prod",
            api_server="https://k8s-prod.trading.company.com",
            version="1.28"
        )
        
        # Staging cluster
        self.clusters["staging"] = ClusterConfig(
            cluster_name="trading-staging",
            environment=ClusterEnvironment.STAGING,
            context="trading-staging",
            namespace="trading-staging",
            api_server="https://k8s-staging.trading.company.com",
            version="1.28"
        )
        
        # Development cluster
        self.clusters["development"] = ClusterConfig(
            cluster_name="trading-dev",
            environment=ClusterEnvironment.DEVELOPMENT,
            context="trading-dev",
            namespace="trading-dev",
            api_server="https://k8s-dev.trading.company.com",
            version="1.28"
        )
    
    def _run_kubectl_command(self, command: List[str], cluster: ClusterConfig, 
                           capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Execute kubectl command
        
        Args:
            command: Kubectl command arguments
            cluster: Target cluster configuration
            capture_output: Whether to capture command output
            
        Returns:
            subprocess.CompletedProcess: Command execution result
        """
        base_cmd = ["kubectl"]
        
        if self.kubeconfig_path:
            base_cmd.extend(["--kubeconfig", self.kubeconfig_path])
        
        base_cmd.extend(["--context", cluster.context])
        base_cmd.extend(["--namespace", cluster.namespace])
        base_cmd.extend(command)
        
        try:
            result = subprocess.run(
                base_cmd,
                capture_output=capture_output,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Kubectl command failed: {result.stderr}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Kubectl command execution failed: {e}")
            raise
    
    def create_namespace(self, cluster: ClusterConfig, namespace: str) -> bool:
        """
        Create Kubernetes namespace
        
        Args:
            cluster: Target cluster
            namespace: Namespace to create
            
        Returns:
            bool: Success status
        """
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": namespace,
                "labels": {
                    "environment": cluster.environment.value,
                    "managed-by": "trading-orchestrator"
                }
            }
        }
        
        return self._apply_manifest(namespace_manifest, cluster)
    
    def deploy_trading_core(self, cluster: ClusterConfig, 
                          image_tag: str, 
                          replicas: int = 3) -> bool:
        """
        Deploy trading core service
        
        Args:
            cluster: Target cluster
            image_tag: Docker image tag
            replicas: Number of replicas
            
        Returns:
            bool: Deployment success status
        """
        logger.info(f"Deploying trading core {image_tag} to {cluster.cluster_name}")
        
        # Create deployment manifest
        deployment = self._create_trading_core_deployment(image_tag, replicas)
        service = self._create_trading_core_service()
        configmap = self._create_trading_configmap()
        
        # Apply manifests
        success = (
            self._apply_manifest(deployment, cluster) and
            self._apply_manifest(service, cluster) and
            self._apply_manifest(configmap, cluster)
        )
        
        if success:
            logger.info(f"Trading core deployment completed successfully")
            self._setup_autoscaling(cluster, "trading-core", 2, 10, 80)
        
        return success
    
    def _create_trading_core_deployment(self, image_tag: str, replicas: int) -> Dict[str, Any]:
        """Create trading core deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "trading-core",
                "labels": {
                    "app": "trading-core",
                    "version": image_tag
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": "trading-core"
                    }
                },
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxSurge": 1,
                        "maxUnavailable": 0
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "trading-core",
                            "version": image_tag
                        },
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8000",
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "trading-core",
                                "image": f"registry.trading.company.com/trading-core:{image_tag}",
                                "ports": [
                                    {"containerPort": 8000, "name": "http"},
                                    {"containerPort": 8001, "name": "metrics"}
                                ],
                                "env": [
                                    {"name": "ENVIRONMENT", "value": "production"},
                                    {"name": "LOG_LEVEL", "value": "INFO"},
                                    {"name": "KAFKA_BROKERS", "value": "kafka:9092"},
                                    {"name": "REDIS_HOST", "value": "redis-master"}
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "200m",
                                        "memory": "256Mi"
                                    },
                                    "limits": {
                                        "cpu": "1000m",
                                        "memory": "1Gi"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ],
                        "affinity": {
                            "podAntiAffinity": {
                                "preferredDuringSchedulingIgnoredDuringExecution": [
                                    {
                                        "weight": 100,
                                        "podAffinityTerm": {
                                            "labelSelector": {
                                                "matchExpressions": [
                                                    {
                                                        "key": "app",
                                                        "operator": "In",
                                                        "values": ["trading-core"]
                                                    }
                                                ]
                                            },
                                            "topologyKey": "kubernetes.io/hostname"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    
    def _create_trading_core_service(self) -> Dict[str, Any]:
        """Create trading core service manifest"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "trading-core",
                "labels": {
                    "app": "trading-core"
                }
            },
            "spec": {
                "selector": {
                    "app": "trading-core"
                },
                "ports": [
                    {
                        "name": "http",
                        "port": 8000,
                        "targetPort": 8000
                    },
                    {
                        "name": "metrics",
                        "port": 8001,
                        "targetPort": 8001
                    }
                ],
                "type": "ClusterIP"
            }
        }
    
    def _create_trading_configmap(self) -> Dict[str, Any]:
        """Create trading configuration configmap"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "trading-config"
            },
            "data": {
                "trading-config.yaml": """
                trading:
                  risk_limits:
                    max_position_size: 1000000
                    max_daily_loss: 50000
                    max_drawdown: 0.1
                  
                  execution:
                    venues: ["NYSE", "NASDAQ", "BATS"]
                    default_slippage: 0.001
                  
                  monitoring:
                    metrics_port: 8001
                    health_check_interval: 30
                """
            }
        }
    
    def _apply_manifest(self, manifest: Dict[str, Any], cluster: ClusterConfig) -> bool:
        """
        Apply Kubernetes manifest
        
        Args:
            manifest: Kubernetes resource manifest
            cluster: Target cluster
            
        Returns:
            bool: Success status
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            yaml.dump(manifest, temp_file)
            temp_file.flush()
            
            result = self._run_kubectl_command(["apply", "-f", temp_file.name], cluster)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
            
            return result.returncode == 0
    
    def _setup_autoscaling(self, cluster: ClusterConfig, deployment_name: str,
                         min_replicas: int, max_replicas: int, target_cpu: int) -> bool:
        """
        Setup horizontal pod autoscaling
        
        Args:
            cluster: Target cluster
            deployment_name: Name of deployment to scale
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            target_cpu: Target CPU utilization percentage
            
        Returns:
            bool: Success status
        """
        hpa_manifest = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{deployment_name}-hpa"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": deployment_name
                },
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": target_cpu
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": 300,
                        "policies": [
                            {
                                "type": "Pods",
                                "value": 1,
                                "periodSeconds": 60
                            }
                        ]
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": 60,
                        "policies": [
                            {
                                "type": "Pods",
                                "value": 2,
                                "periodSeconds": 30
                            }
                        ]
                    }
                }
            }
        }
        
        return self._apply_manifest(hpa_manifest, cluster)
    
    def deploy_database_services(self, cluster: ClusterConfig) -> bool:
        """
        Deploy database and caching services
        
        Args:
            cluster: Target cluster
            
        Returns:
            bool: Deployment success status
        """
        logger.info(f"Deploying database services to {cluster.cluster_name}")
        
        # PostgreSQL StatefulSet
        postgres_manifest = self._create_postgres_manifest()
        
        # Redis deployment
        redis_manifest = self._create_redis_manifest()
        
        # Kafka cluster
        kafka_manifest = self._create_kafka_manifest()
        
        success = (
            self._apply_manifest(postgres_manifest, cluster) and
            self._apply_manifest(redis_manifest, cluster) and
            self._apply_manifest(kafka_manifest, cluster)
        )
        
        if success:
            logger.info("Database services deployed successfully")
        
        return success
    
    def _create_postgres_manifest(self) -> Dict[str, Any]:
        """Create PostgreSQL statefulset manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "postgres"
            },
            "spec": {
                "serviceName": "postgres",
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "postgres"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "postgres"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "postgres",
                                "image": "postgres:15-alpine",
                                "env": [
                                    {
                                        "name": "POSTGRES_DB",
                                        "value": "trading"
                                    },
                                    {
                                        "name": "POSTGRES_USER",
                                        "value": "trading_user"
                                    },
                                    {
                                        "name": "POSTGRES_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "postgres-secret",
                                                "key": "password"
                                            }
                                        }
                                    }
                                ],
                                "ports": [
                                    {
                                        "containerPort": 5432,
                                        "name": "postgres"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "postgres-data",
                                        "mountPath": "/var/lib/postgresql/data"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "256Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "1Gi"
                                    }
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "postgres-data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": "10Gi"
                                }
                            }
                        }
                    }
                ]
            }
        }
    
    def _create_redis_manifest(self) -> Dict[str, Any]:
        """Create Redis deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "redis"
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "redis"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "redis"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "redis",
                                "image": "redis:7-alpine",
                                "command": ["redis-server", "--appendonly", "yes"],
                                "ports": [
                                    {
                                        "containerPort": 6379,
                                        "name": "redis"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "50m",
                                        "memory": "64Mi"
                                    },
                                    "limits": {
                                        "cpu": "200m",
                                        "memory": "128Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def _create_kafka_manifest(self) -> Dict[str, Any]:
        """Create Kafka deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "kafka"
            },
            "spec": {
                "serviceName": "kafka",
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "kafka"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "kafka"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "kafka",
                                "image": "confluentinc/cp-kafka:7.4.0",
                                "ports": [
                                    {
                                        "containerPort": 9092,
                                        "name": "kafka"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "KAFKA_BROKER_ID",
                                        "value": "1"
                                    },
                                    {
                                        "name": "KAFKA_ZOOKEEPER_CONNECT",
                                        "value": "zookeeper:2181"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "256Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    
    def deploy_monitoring_stack(self, cluster: ClusterConfig) -> bool:
        """
        Deploy monitoring and observability stack
        
        Args:
            cluster: Target cluster
            
        Returns:
            bool: Deployment success status
        """
        logger.info(f"Deploying monitoring stack to {cluster.cluster_name}")
        
        # Prometheus deployment
        prometheus_manifest = self._create_prometheus_manifest()
        
        # Grafana deployment
        grafana_manifest = self._create_grafana_manifest()
        
        success = (
            self._apply_manifest(prometheus_manifest, cluster) and
            self._apply_manifest(grafana_manifest, cluster)
        )
        
        if success:
            logger.info("Monitoring stack deployed successfully")
        
        return success
    
    def _create_prometheus_manifest(self) -> Dict[str, Any]:
        """Create Prometheus deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "prometheus"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "prometheus"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "prometheus"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "prometheus",
                                "image": "prom/prometheus:latest",
                                "ports": [
                                    {
                                        "containerPort": 9090,
                                        "name": "http"
                                    }
                                ],
                                "args": [
                                    "--config.file=/etc/prometheus/prometheus.yml",
                                    "--storage.tsdb.path=/prometheus",
                                    "--web.console.libraries=/etc/prometheus/console_libraries",
                                    "--web.console.templates=/etc/prometheus/consoles",
                                    "--storage.tsdb.retention.time=200h",
                                    "--web.enable-lifecycle"
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "prometheus-config",
                                        "mountPath": "/etc/prometheus"
                                    },
                                    {
                                        "name": "prometheus-data",
                                        "mountPath": "/prometheus"
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "prometheus-config",
                                "configMap": {
                                    "name": "prometheus-config"
                                }
                            },
                            {
                                "name": "prometheus-data",
                                "emptyDir": {}
                            }
                        ]
                    }
                }
            }
        }
    
    def _create_grafana_manifest(self) -> Dict[str, Any]:
        """Create Grafana deployment manifest"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "grafana"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "grafana"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "grafana"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "grafana",
                                "image": "grafana/grafana:latest",
                                "ports": [
                                    {
                                        "containerPort": 3000,
                                        "name": "http"
                                    }
                                ],
                                "env": [
                                    {
                                        "name": "GF_SECURITY_ADMIN_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "grafana-secret",
                                                "key": "admin-password"
                                            }
                                        }
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "grafana-data",
                                        "mountPath": "/var/lib/grafana"
                                    }
                                ]
                            }
                        ],
                        "volumes": [
                            {
                                "name": "grafana-data",
                                "emptyDir": {}
                            }
                        ]
                    }
                }
            }
        }
    
    def check_deployment_status(self, cluster: ClusterConfig, deployment_name: str) -> Dict[str, Any]:
        """
        Check deployment status
        
        Args:
            cluster: Target cluster
            deployment_name: Name of deployment to check
            
        Returns:
            Dict: Deployment status information
        """
        result = self._run_kubectl_command(
            ["get", "deployment", deployment_name, "-o", "json"], 
            cluster
        )
        
        if result.returncode == 0:
            deployment_info = json.loads(result.stdout)
            return {
                "available_replicas": deployment_info["status"].get("availableReplicas", 0),
                "ready_replicas": deployment_info["status"].get("readyReplicas", 0),
                "updated_replicas": deployment_info["status"].get("updatedReplicas", 0),
                "replicas": deployment_info["status"].get("replicas", 0),
                "conditions": deployment_info["status"].get("conditions", [])
            }
        else:
            return {"error": f"Failed to get deployment status: {result.stderr}"}
    
    def scale_deployment(self, cluster: ClusterConfig, deployment_name: str, replicas: int) -> bool:
        """
        Scale deployment to specified number of replicas
        
        Args:
            cluster: Target cluster
            deployment_name: Name of deployment to scale
            replicas: Number of replicas
            
        Returns:
            bool: Success status
        """
        result = self._run_kubectl_command(
            ["scale", "deployment", deployment_name, f"--replicas={replicas}"],
            cluster
        )
        
        if result.returncode == 0:
            logger.info(f"Scaled deployment {deployment_name} to {replicas} replicas")
            return True
        else:
            logger.error(f"Failed to scale deployment: {result.stderr}")
            return False
    
    def get_cluster_metrics(self, cluster: ClusterConfig) -> Dict[str, Any]:
        """
        Get cluster resource metrics
        
        Args:
            cluster: Target cluster
            
        Returns:
            Dict: Cluster metrics
        """
        # Get node metrics
        nodes_result = self._run_kubectl_command(["top", "nodes"], cluster)
        pods_result = self._run_kubectl_command(["top", "pods"], cluster)
        
        metrics = {
            "cluster_name": cluster.cluster_name,
            "environment": cluster.environment.value,
            "timestamp": datetime.now().isoformat(),
            "node_metrics": self._parse_top_output(nodes_result.stdout) if nodes_result.returncode == 0 else {},
            "pod_metrics": self._parse_top_output(pods_result.stdout) if pods_result.returncode == 0 else {},
        }
        
        return metrics
    
    def _parse_top_output(self, output: str) -> List[Dict[str, str]]:
        """
        Parse kubectl top command output
        
        Args:
            output: Command output string
            
        Returns:
            List: Parsed metrics
        """
        lines = output.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split()
        metrics = []
        
        for line in lines[1:]:
            values = line.split()
            if len(values) == len(headers):
                metric = {headers[i]: values[i] for i in range(len(headers))}
                metrics.append(metric)
        
        return metrics
    
    def perform_rolling_update(self, cluster: ClusterConfig, deployment_name: str, 
                             new_image_tag: str) -> bool:
        """
        Perform rolling update of deployment
        
        Args:
            cluster: Target cluster
            deployment_name: Name of deployment to update
            new_image_tag: New Docker image tag
            
        Returns:
            bool: Success status
        """
        logger.info(f"Performing rolling update of {deployment_name} to {new_image_tag}")
        
        result = self._run_kubectl_command([
            "set", "image", f"deployment/{deployment_name}", 
            f"{deployment_name}=registry.trading.company.com/{deployment_name}:{new_image_tag}"
        ], cluster)
        
        if result.returncode == 0:
            # Wait for rollout to complete
            return self._wait_for_rollout(cluster, deployment_name)
        else:
            logger.error(f"Rolling update failed: {result.stderr}")
            return False
    
    def _wait_for_rollout(self, cluster: ClusterConfig, deployment_name: str, 
                         timeout: int = 300) -> bool:
        """
        Wait for deployment rollout to complete
        
        Args:
            cluster: Target cluster
            deployment_name: Name of deployment
            timeout: Timeout in seconds
            
        Returns:
            bool: Rollout success status
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_deployment_status(cluster, deployment_name)
            
            if "error" in status:
                return False
            
            available = status.get("available_replicas", 0)
            updated = status.get("updated_replicas", 0)
            replicas = status.get("replicas", 0)
            
            if available == replicas and updated == replicas:
                logger.info(f"Rollout completed successfully for {deployment_name}")
                return True
            
            time.sleep(5)
        
        logger.error(f"Rollout timeout for {deployment_name}")
        return False

# Example usage and testing
if __name__ == "__main__":
    # Example implementation
    orchestrator = KubernetesOrchestrator()
    
    # Deploy to staging environment
    staging_cluster = orchestrator.clusters["staging"]
    
    try:
        # Create namespace
        orchestrator.create_namespace(staging_cluster, "trading-staging")
        
        # Deploy database services
        orchestrator.deploy_database_services(staging_cluster)
        
        # Deploy trading core
        orchestrator.deploy_trading_core(staging_cluster, "v1.2.3", replicas=2)
        
        # Deploy monitoring
        orchestrator.deploy_monitoring_stack(staging_cluster)
        
        # Check deployment status
        status = orchestrator.check_deployment_status(staging_cluster, "trading-core")
        print(f"Trading core status: {status}")
        
        # Get cluster metrics
        metrics = orchestrator.get_cluster_metrics(staging_cluster)
        print(f"Cluster metrics collected: {len(metrics.get('pod_metrics', []))} pods")
        
    except Exception as e:
        logger.error(f"Kubernetes deployment failed: {e}")
        raise