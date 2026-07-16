"""Slack MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)


class SlackMCP(BaseMCPServer):
    """Slack MCP server for team communication and incident coordination."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Slack MCP server."""
        super().__init__("Slack", MCPCategory.COMMS, config)
        self.client = None
        self.channel = config.get('channel', '#incidents')
        
    async def _connect(self):
        """Connect to Slack API."""
        try:
            self.client = WebClient(token=self.config.get('bot_token'))
            # Test the connection
            response = self.client.auth_test()
            logger.info(f"Connected to Slack as {response['user']}")
        except Exception as e:
            logger.error(f"Failed to connect to Slack: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Slack state.
        
        Returns:
            Recent messages, thread context, and channel activity
        """
        try:
            # Get channel ID from channel name
            channels = self.client.conversations_list(types="public_channel,private_channel")
            channel_id = None
            for channel in channels['channels']:
                if channel['name'] == self.channel.lstrip('#'):
                    channel_id = channel['id']
                    break
            
            if not channel_id:
                return {"error": f"Channel {self.channel} not found", "status": "unhealthy"}
            
            # Get recent messages
            history = self.client.conversations_history(channel=channel_id, limit=20)
            messages = []
            
            for msg in history['messages']:
                messages.append({
                    "text": msg.get('text', ''),
                    "user": msg.get('user', 'unknown'),
                    "timestamp": msg.get('ts'),
                    "thread_ts": msg.get('thread_ts'),
                    "reply_count": msg.get('reply_count', 0)
                })
            
            # Get channel info
            channel_info = self.client.conversations_info(channel=channel_id)
            
            return {
                "status": "healthy",
                "channel": self.channel,
                "channel_id": channel_id,
                "member_count": channel_info['channel'].get('num_members', 0),
                "recent_messages": messages,
                "is_archived": channel_info['channel'].get('is_archived', False)
            }
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "post_message":
                return await self._post_message(params)
            elif action == "update_message":
                return await self._update_message(params)
            elif action == "post_thread_reply":
                return await self._post_thread_reply(params)
            elif action == "add_reaction":
                return await self._add_reaction(params)
            elif action == "create_channel":
                return await self._create_channel(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _post_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Post a message to a channel."""
        channel = params.get('channel', self.channel)
        text = params.get('text')
        blocks = params.get('blocks')
        
        response = self.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )
        
        return {
            "success": True,
            "message": "Message posted",
            "ts": response['ts'],
            "channel": response['channel']
        }
    
    async def _update_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing message."""
        channel = params.get('channel', self.channel)
        ts = params.get('ts')
        text = params.get('text')
        blocks = params.get('blocks')
        
        response = self.client.chat_update(
            channel=channel,
            ts=ts,
            text=text,
            blocks=blocks
        )
        
        return {"success": True, "message": "Message updated"}
    
    async def _post_thread_reply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Post a reply in a thread."""
        channel = params.get('channel', self.channel)
        thread_ts = params.get('thread_ts')
        text = params.get('text')
        
        response = self.client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=text
        )
        
        return {"success": True, "message": "Thread reply posted", "ts": response['ts']}
    
    async def _add_reaction(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a reaction to a message."""
        channel = params.get('channel', self.channel)
        timestamp = params.get('timestamp')
        reaction = params.get('reaction')
        
        self.client.reactions_add(
            channel=channel,
            timestamp=timestamp,
            name=reaction
        )
        
        return {"success": True, "message": f"Reaction '{reaction}' added"}
    
    async def _create_channel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new channel."""
        name = params.get('name')
        is_private = params.get('is_private', False)
        
        response = self.client.conversations_create(
            name=name,
            is_private=is_private
        )
        
        return {
            "success": True,
            "message": f"Channel '{name}' created",
            "channel_id": response['channel']['id']
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Slack-specific health check."""
        try:
            response = self.client.auth_test()
            return {
                "user": response['user'],
                "team": response['team'],
                "message": "Slack API accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Slack capabilities."""
        return [
            "post_message",
            "update_message",
            "post_thread_reply",
            "add_reaction",
            "create_channel",
            "read_messages",
            "read_thread"
        ]
