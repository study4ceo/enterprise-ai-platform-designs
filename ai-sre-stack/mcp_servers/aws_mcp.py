"""AWS MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class AWSMCP(BaseMCPServer):
    """AWS MCP server for cloud resource, IAM, and cost management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize AWS MCP server."""
        super().__init__("AWS", MCPCategory.INFRA, config)
        self.ec2_client = None
        self.iam_client = None
        self.ce_client = None
        self.cloudwatch_client = None
        self.region = config.get('region', 'us-east-1')
        
    async def _connect(self):
        """Connect to AWS services."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.get('access_key_id'),
                aws_secret_access_key=self.config.get('secret_access_key'),
                region_name=self.region
            )
            
            self.ec2_client = session.client('ec2')
            self.iam_client = session.client('iam')
            self.ce_client = session.client('ce')
            self.cloudwatch_client = session.client('cloudwatch')
            
            logger.info(f"Connected to AWS in region {self.region}")
        except Exception as e:
            logger.error(f"Failed to connect to AWS: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current AWS state.
        
        Returns:
            Current state including instances, costs, and service health
        """
        try:
            # Get EC2 instances
            instances = self.ec2_client.describe_instances()
            instance_status = []
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    instance_status.append({
                        "instance_id": instance['InstanceId'],
                        "type": instance['InstanceType'],
                        "state": instance['State']['Name'],
                        "launch_time": str(instance['LaunchTime']),
                        "tags": {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })
            
            # Get cost and usage (last 7 days)
            import datetime
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=7)
            
            cost_data = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            
            costs = []
            for result in cost_data['ResultsByTime']:
                costs.append({
                    "date": result['TimePeriod']['Start'],
                    "amount": float(result['Total']['UnblendedCost']['Amount']),
                    "unit": result['Total']['UnblendedCost']['Unit']
                })
            
            # Get IAM users count
            iam_users = self.iam_client.list_users()
            user_count = len(iam_users['Users'])
            
            return {
                "instances": instance_status,
                "costs": costs,
                "iam_users_count": user_count,
                "region": self.region,
                "status": "healthy"
            }
            
        except ClientError as e:
            logger.error(f"AWS API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AWS action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "start_instance":
                return await self._start_instance(params)
            elif action == "stop_instance":
                return await self._stop_instance(params)
            elif action == "terminate_instance":
                return await self._terminate_instance(params)
            elif action == "get_metrics":
                return await self._get_cloudwatch_metrics(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _start_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start an EC2 instance."""
        instance_id = params.get('instance_id')
        
        response = self.ec2_client.start_instances(InstanceIds=[instance_id])
        return {"success": True, "message": f"Instance {instance_id} started", "response": response}
    
    async def _stop_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop an EC2 instance."""
        instance_id = params.get('instance_id')
        
        response = self.ec2_client.stop_instances(InstanceIds=[instance_id])
        return {"success": True, "message": f"Instance {instance_id} stopped", "response": response}
    
    async def _terminate_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate an EC2 instance."""
        instance_id = params.get('instance_id')
        
        response = self.ec2_client.terminate_instances(InstanceIds=[instance_id])
        return {"success": True, "message": f"Instance {instance_id} terminated", "response": response}
    
    async def _get_cloudwatch_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CloudWatch metrics for an instance."""
        instance_id = params.get('instance_id')
        metric_name = params.get('metric_name', 'CPUUtilization')
        
        import datetime
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            EndTime=datetime.datetime.utcnow(),
            Period=300,
            Statistics=['Average']
        )
        
        return {"success": True, "metrics": response['Datapoints']}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform AWS-specific health check."""
        try:
            # Check if we can describe regions
            regions = self.ec2_client.describe_regions()
            return {
                "regions_accessible": len(regions['Regions']),
                "message": "AWS API accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available AWS capabilities."""
        return [
            "start_instance",
            "stop_instance",
            "terminate_instance",
            "get_metrics",
            "observe_instances",
            "observe_costs",
            "observe_iam"
        ]
