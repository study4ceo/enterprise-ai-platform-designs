"""AWS CloudTrail MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CloudTrailMCP(BaseMCPServer):
    """AWS CloudTrail MCP server for audit logging and API activity monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CloudTrail MCP server."""
        super().__init__("AWS CloudTrail", MCPCategory.OBSERVABILITY, config)
        self.cloudtrail_client = None
        self.logs_client = None
        self.region = config.get('region', 'us-east-1')
        self.trail_name = config.get('trail_name')
        
    async def _connect(self):
        """Connect to AWS CloudTrail."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.get('access_key_id'),
                aws_secret_access_key=self.config.get('secret_access_key'),
                region_name=self.region
            )
            
            self.cloudtrail_client = session.client('cloudtrail')
            self.logs_client = session.client('logs')
            
            logger.info(f"Connected to CloudTrail in region {self.region}")
                
        except Exception as e:
            logger.error(f"Failed to connect to CloudTrail: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe CloudTrail activity and audit logs.
        
        Returns:
            Recent API activity, security-relevant events, and anomalies
        """
        try:
            # Get trail status
            trails = []
            trail_status_summary = {"logging": 0, "not_logging": 0}
            
            trails_response = self.cloudtrail_client.describe_trails()
            for trail in trails_response.get('trailList', []):
                status = self.cloudtrail_client.get_trail_status(Name=trail['Name'])
                
                is_logging = status.get('IsLogging', False)
                if is_logging:
                    trail_status_summary["logging"] += 1
                else:
                    trail_status_summary["not_logging"] += 1
                
                trails.append({
                    "name": trail['Name'],
                    "is_logging": is_logging,
                    "s3_bucket": trail.get('S3BucketName'),
                    "is_multi_region": trail.get('IsMultiRegionTrail', False),
                    "is_organization_trail": trail.get('IsOrganizationTrail', False),
                    "last_delivery": str(status.get('LatestDeliveryTime', 'N/A'))
                })
            
            # Get recent events (last 15 minutes)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=15)
            
            events_response = self.cloudtrail_client.lookup_events(
                StartTime=start_time,
                EndTime=end_time,
                MaxResults=50
            )
            
            # Analyze events
            events = []
            event_types = {}
            users = set()
            error_count = 0
            security_relevant_count = 0
            
            security_events = [
                'CreateAccessKey', 'DeleteAccessKey', 'CreateUser', 'DeleteUser',
                'PutUserPolicy', 'DeleteUserPolicy', 'AttachUserPolicy', 'DetachUserPolicy',
                'CreateRole', 'DeleteRole', 'PutRolePolicy', 'DeleteRolePolicy',
                'CreateBucket', 'DeleteBucket', 'PutBucketPolicy',
                'AuthorizeSecurityGroupIngress', 'AuthorizeSecurityGroupEgress',
                'RevokeSecurityGroupIngress', 'RevokeSecurityGroupEgress',
                'StopInstances', 'TerminateInstances', 'ModifyInstanceAttribute',
                'ConsoleLogin', 'AssumeRole'
            ]
            
            for event in events_response.get('Events', []):
                event_name = event.get('EventName')
                username = event.get('Username', 'Unknown')
                
                # Track event types
                event_types[event_name] = event_types.get(event_name, 0) + 1
                users.add(username)
                
                # Check for errors
                if event.get('ErrorCode') or event.get('ErrorMessage'):
                    error_count += 1
                
                # Check if security-relevant
                is_security_relevant = event_name in security_events
                if is_security_relevant:
                    security_relevant_count += 1
                
                events.append({
                    "event_id": event['EventId'],
                    "event_name": event_name,
                    "event_time": str(event['EventTime']),
                    "username": username,
                    "event_source": event.get('EventSource'),
                    "resources": [r.get('ResourceName', 'Unknown') for r in event.get('Resources', [])],
                    "source_ip": event.get('SourceIPAddress'),
                    "user_agent": event.get('UserAgent'),
                    "error_code": event.get('ErrorCode'),
                    "error_message": event.get('ErrorMessage'),
                    "is_security_relevant": is_security_relevant
                })
            
            # Detect anomalies
            anomalies = []
            
            # Anomaly 1: High error rate
            if error_count > 10:
                anomalies.append({
                    "type": "high_error_rate",
                    "severity": "medium",
                    "description": f"{error_count} failed API calls in last 15 minutes"
                })
            
            # Anomaly 2: Security-relevant activity spike
            if security_relevant_count > 5:
                anomalies.append({
                    "type": "security_activity_spike",
                    "severity": "high",
                    "description": f"{security_relevant_count} security-relevant events detected"
                })
            
            # Anomaly 3: Root account usage
            if 'Root' in users or 'root' in users:
                anomalies.append({
                    "type": "root_account_usage",
                    "severity": "critical",
                    "description": "Root account activity detected (best practice: avoid root usage)"
                })
            
            # Determine overall status
            overall_status = "healthy"
            if any(a['severity'] == 'critical' for a in anomalies):
                overall_status = "critical"
            elif any(a['severity'] == 'high' for a in anomalies):
                overall_status = "unhealthy"
            elif trail_status_summary["not_logging"] > 0:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "trails": trails,
                "trail_summary": trail_status_summary,
                "recent_events": events[:20],  # Limit to 20
                "total_events": len(events),
                "event_type_breakdown": dict(sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]),
                "unique_users": len(users),
                "error_count": error_count,
                "security_relevant_count": security_relevant_count,
                "anomalies": anomalies,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            }
            
        except ClientError as e:
            logger.error(f"CloudTrail API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CloudTrail action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "start_logging":
                return await self._start_logging(params)
            elif action == "stop_logging":
                return await self._stop_logging(params)
            elif action == "lookup_events":
                return await self._lookup_events(params)
            elif action == "get_event_details":
                return await self._get_event_details(params)
            elif action == "create_trail":
                return await self._create_trail(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _start_logging(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start logging for a CloudTrail trail."""
        trail_name = params.get('trail_name', self.trail_name)
        
        if not trail_name:
            return {"error": "No trail name provided", "success": False}
        
        self.cloudtrail_client.start_logging(Name=trail_name)
        
        return {
            "success": True,
            "message": f"Started logging for trail: {trail_name}"
        }
    
    async def _stop_logging(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop logging for a CloudTrail trail."""
        trail_name = params.get('trail_name', self.trail_name)
        
        if not trail_name:
            return {"error": "No trail name provided", "success": False}
        
        self.cloudtrail_client.stop_logging(Name=trail_name)
        
        return {
            "success": True,
            "message": f"Stopped logging for trail: {trail_name}"
        }
    
    async def _lookup_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lookup specific CloudTrail events."""
        # Time range
        end_time = params.get('end_time', datetime.utcnow())
        start_time = params.get('start_time', end_time - timedelta(hours=1))
        
        # Filters
        lookup_attributes = []
        if params.get('username'):
            lookup_attributes.append({
                'AttributeKey': 'Username',
                'AttributeValue': params['username']
            })
        if params.get('event_name'):
            lookup_attributes.append({
                'AttributeKey': 'EventName',
                'AttributeValue': params['event_name']
            })
        if params.get('resource_name'):
            lookup_attributes.append({
                'AttributeKey': 'ResourceName',
                'AttributeValue': params['resource_name']
            })
        
        # Query CloudTrail
        query_params = {
            'StartTime': start_time,
            'EndTime': end_time,
            'MaxResults': params.get('max_results', 50)
        }
        
        if lookup_attributes:
            query_params['LookupAttributes'] = lookup_attributes
        
        response = self.cloudtrail_client.lookup_events(**query_params)
        
        return {
            "success": True,
            "events": response.get('Events', []),
            "event_count": len(response.get('Events', []))
        }
    
    async def _get_event_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific event."""
        event_id = params.get('event_id')
        
        if not event_id:
            return {"error": "No event ID provided", "success": False}
        
        # Lookup the specific event
        response = self.cloudtrail_client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventId',
                    'AttributeValue': event_id
                }
            ]
        )
        
        events = response.get('Events', [])
        if events:
            return {
                "success": True,
                "event": events[0]
            }
        else:
            return {
                "success": False,
                "error": f"Event {event_id} not found"
            }
    
    async def _create_trail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new CloudTrail trail."""
        trail_name = params.get('trail_name')
        s3_bucket = params.get('s3_bucket')
        
        if not trail_name or not s3_bucket:
            return {"error": "Trail name and S3 bucket are required", "success": False}
        
        trail_config = {
            'Name': trail_name,
            'S3BucketName': s3_bucket,
            'IsMultiRegionTrail': params.get('is_multi_region', True),
            'IncludeGlobalServiceEvents': params.get('include_global_events', True)
        }
        
        response = self.cloudtrail_client.create_trail(**trail_config)
        
        # Start logging automatically
        self.cloudtrail_client.start_logging(Name=trail_name)
        
        return {
            "success": True,
            "message": f"Created and started trail: {trail_name}",
            "trail_arn": response['TrailARN']
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform CloudTrail-specific health check."""
        try:
            trails = self.cloudtrail_client.describe_trails()
            trail_count = len(trails.get('trailList', []))
            
            return {
                "trail_count": trail_count,
                "message": "CloudTrail accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available CloudTrail capabilities."""
        return [
            "start_logging",
            "stop_logging",
            "lookup_events",
            "get_event_details",
            "create_trail",
            "monitor_api_activity",
            "detect_anomalies"
        ]
