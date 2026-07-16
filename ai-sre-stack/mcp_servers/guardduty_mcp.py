"""AWS GuardDuty MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GuardDutyMCP(BaseMCPServer):
    """AWS GuardDuty MCP server for threat detection and security monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize GuardDuty MCP server."""
        super().__init__("AWS GuardDuty", MCPCategory.OBSERVABILITY, config)
        self.guardduty_client = None
        self.detector_id = None
        self.region = config.get('region', 'us-east-1')
        
    async def _connect(self):
        """Connect to AWS GuardDuty."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.get('access_key_id'),
                aws_secret_access_key=self.config.get('secret_access_key'),
                region_name=self.region
            )
            
            self.guardduty_client = session.client('guardduty')
            
            # Get detector ID (required for GuardDuty operations)
            detectors = self.guardduty_client.list_detectors()
            if detectors['DetectorIds']:
                self.detector_id = detectors['DetectorIds'][0]
                logger.info(f"Connected to GuardDuty: detector {self.detector_id}")
            else:
                raise Exception("No GuardDuty detector found. Please enable GuardDuty first.")
                
        except Exception as e:
            logger.error(f"Failed to connect to GuardDuty: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current GuardDuty findings and security events.
        
        Returns:
            Current security findings, threat intelligence, and risk assessment
        """
        try:
            # Get active findings
            findings_response = self.guardduty_client.list_findings(
                DetectorId=self.detector_id,
                FindingCriteria={
                    'Criterion': {
                        'service.archived': {
                            'Eq': ['false']
                        }
                    }
                },
                MaxResults=50
            )
            
            finding_ids = findings_response.get('FindingIds', [])
            
            # Get detailed findings
            findings = []
            critical_count = 0
            high_count = 0
            medium_count = 0
            low_count = 0
            
            if finding_ids:
                detailed_findings = self.guardduty_client.get_findings(
                    DetectorId=self.detector_id,
                    FindingIds=finding_ids
                )
                
                for finding in detailed_findings.get('Findings', []):
                    severity = finding.get('Severity', 0)
                    
                    # Count by severity
                    if severity >= 7.0:
                        critical_count += 1
                        severity_label = "CRITICAL"
                    elif severity >= 4.0:
                        high_count += 1
                        severity_label = "HIGH"
                    elif severity >= 1.0:
                        medium_count += 1
                        severity_label = "MEDIUM"
                    else:
                        low_count += 1
                        severity_label = "LOW"
                    
                    findings.append({
                        "id": finding['Id'],
                        "type": finding['Type'],
                        "severity": severity,
                        "severity_label": severity_label,
                        "title": finding['Title'],
                        "description": finding['Description'],
                        "created_at": str(finding['CreatedAt']),
                        "updated_at": str(finding['UpdatedAt']),
                        "region": finding['Region'],
                        "account_id": finding['AccountId'],
                        "resource": self._extract_resource_info(finding),
                        "action": self._extract_action_info(finding)
                    })
            
            # Get detector status
            detector_info = self.guardduty_client.get_detector(DetectorId=self.detector_id)
            
            # Determine overall status
            overall_status = "healthy"
            if critical_count > 0:
                overall_status = "critical"
            elif high_count > 0:
                overall_status = "unhealthy"
            elif medium_count > 0:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "detector_id": self.detector_id,
                "detector_status": detector_info['Status'],
                "findings": findings[:20],  # Limit to 20 most recent
                "total_findings": len(findings),
                "severity_breakdown": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count
                },
                "region": self.region,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except ClientError as e:
            logger.error(f"GuardDuty API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    def _extract_resource_info(self, finding: Dict) -> Dict[str, Any]:
        """Extract resource information from finding."""
        resource = finding.get('Resource', {})
        
        resource_info = {
            "type": resource.get('ResourceType', 'Unknown')
        }
        
        # Extract instance details if available
        if 'InstanceDetails' in resource:
            instance = resource['InstanceDetails']
            resource_info['instance_id'] = instance.get('InstanceId')
            resource_info['instance_type'] = instance.get('InstanceType')
            resource_info['availability_zone'] = instance.get('AvailabilityZone')
            
            # Get tags
            if 'Tags' in instance:
                resource_info['tags'] = {tag['Key']: tag['Value'] for tag in instance['Tags']}
        
        # Extract S3 bucket details if available
        if 'S3BucketDetails' in resource:
            buckets = resource['S3BucketDetails']
            resource_info['buckets'] = [bucket['Name'] for bucket in buckets]
        
        return resource_info
    
    def _extract_action_info(self, finding: Dict) -> Dict[str, Any]:
        """Extract action information from finding."""
        service = finding.get('Service', {})
        action = service.get('Action', {})
        
        action_info = {
            "type": action.get('ActionType', 'Unknown')
        }
        
        # Extract network connection details
        if 'NetworkConnectionAction' in action:
            network = action['NetworkConnectionAction']
            action_info['network'] = {
                "protocol": network.get('Protocol'),
                "local_port": network.get('LocalPortDetails', {}).get('Port'),
                "remote_ip": network.get('RemoteIpDetails', {}).get('IpAddressV4'),
                "remote_country": network.get('RemoteIpDetails', {}).get('Country', {}).get('CountryName'),
                "blocked": network.get('Blocked', False)
            }
        
        # Extract API call details
        if 'AwsApiCallAction' in action:
            api_call = action['AwsApiCallAction']
            action_info['api_call'] = {
                "api": api_call.get('Api'),
                "service": api_call.get('ServiceName'),
                "caller_type": api_call.get('CallerType'),
                "remote_ip": api_call.get('RemoteIpDetails', {}).get('IpAddressV4')
            }
        
        return action_info
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GuardDuty action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "archive_findings":
                return await self._archive_findings(params)
            elif action == "unarchive_findings":
                return await self._unarchive_findings(params)
            elif action == "get_finding_details":
                return await self._get_finding_details(params)
            elif action == "create_sample_findings":
                return await self._create_sample_findings(params)
            elif action == "update_findings_feedback":
                return await self._update_findings_feedback(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _archive_findings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive GuardDuty findings (mark as resolved)."""
        finding_ids = params.get('finding_ids', [])
        
        if not finding_ids:
            return {"error": "No finding IDs provided", "success": False}
        
        self.guardduty_client.archive_findings(
            DetectorId=self.detector_id,
            FindingIds=finding_ids
        )
        
        return {
            "success": True,
            "message": f"Archived {len(finding_ids)} findings",
            "finding_ids": finding_ids
        }
    
    async def _unarchive_findings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unarchive GuardDuty findings."""
        finding_ids = params.get('finding_ids', [])
        
        if not finding_ids:
            return {"error": "No finding IDs provided", "success": False}
        
        self.guardduty_client.unarchive_findings(
            DetectorId=self.detector_id,
            FindingIds=finding_ids
        )
        
        return {
            "success": True,
            "message": f"Unarchived {len(finding_ids)} findings",
            "finding_ids": finding_ids
        }
    
    async def _get_finding_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about specific findings."""
        finding_ids = params.get('finding_ids', [])
        
        if not finding_ids:
            return {"error": "No finding IDs provided", "success": False}
        
        response = self.guardduty_client.get_findings(
            DetectorId=self.detector_id,
            FindingIds=finding_ids
        )
        
        return {
            "success": True,
            "findings": response.get('Findings', [])
        }
    
    async def _create_sample_findings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sample findings for testing (GuardDuty feature)."""
        finding_types = params.get('finding_types', [
            'Recon:EC2/PortProbeUnprotectedPort',
            'UnauthorizedAccess:EC2/TorIPCaller'
        ])
        
        response = self.guardduty_client.create_sample_findings(
            DetectorId=self.detector_id,
            FindingTypes=finding_types
        )
        
        return {
            "success": True,
            "message": "Sample findings created for testing"
        }
    
    async def _update_findings_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update feedback for findings (useful/not useful)."""
        finding_ids = params.get('finding_ids', [])
        feedback = params.get('feedback', 'USEFUL')  # USEFUL or NOT_USEFUL
        
        if not finding_ids:
            return {"error": "No finding IDs provided", "success": False}
        
        self.guardduty_client.update_findings_feedback(
            DetectorId=self.detector_id,
            FindingIds=finding_ids,
            Feedback=feedback
        )
        
        return {
            "success": True,
            "message": f"Updated feedback to {feedback} for {len(finding_ids)} findings"
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform GuardDuty-specific health check."""
        try:
            if self.detector_id:
                detector_info = self.guardduty_client.get_detector(DetectorId=self.detector_id)
                return {
                    "detector_status": detector_info['Status'],
                    "message": "GuardDuty accessible"
                }
            else:
                return {"error": "No detector configured"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available GuardDuty capabilities."""
        return [
            "archive_findings",
            "unarchive_findings",
            "get_finding_details",
            "create_sample_findings",
            "update_findings_feedback",
            "list_findings",
            "monitor_threats"
        ]
