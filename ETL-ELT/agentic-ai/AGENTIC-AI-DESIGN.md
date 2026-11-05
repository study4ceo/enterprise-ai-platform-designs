# Agentic AI Architecture with LangGraph, LangChain & MCP

## Overview
Comprehensive architecture for building autonomous AI agents using LangGraph for workflows, LangChain for orchestration, LangSmith for monitoring, and MCP (Model Context Protocol) servers for tool integration.

---

## Core Concepts

### What is Agentic AI?
AI systems that can:
- **Plan**: Break down complex tasks into steps
- **Act**: Use tools and APIs to accomplish goals
- **Observe**: Monitor results and adapt behavior
- **Remember**: Maintain context across interactions
- **Collaborate**: Work with other agents and humans

### Architecture Stack

```
┌─────────────────────────────────────────────────────────────┐
│  User Interface                                              │
│  - Web App, Slack Bot, API                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Orchestration (LangGraph)                             │
│  - State management                                          │
│  - Workflow definition                                       │
│  - Decision routing                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Framework (LangChain)                                 │
│  - Tool integration                                          │
│  - Memory management                                         │
│  - Prompt templates                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LLM Layer (Bedrock/OpenAI)                                  │
│  - Claude 3 Sonnet/Opus                                      │
│  - GPT-4                                                     │
│  - Function calling                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Tool Layer (MCP Servers)                                    │
│  - Database access                                           │
│  - API integrations                                          │
│  - File operations                                           │
│  - Web search                                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Observability (LangSmith)                                   │
│  - Tracing                                                   │
│  - Debugging                                                 │
│  - Analytics                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## LangChain Fundamentals

### Basic Agent Setup

```python
from langchain_community.llms import Bedrock
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import boto3

# Initialize LLM
llm = Bedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"max_tokens": 4096, "temperature": 0}
)

# Define tools
def search_database(query: str) -> str:
    """Search database for information."""
    # Implementation
    return f"Database results for: {query}"

def web_search(query: str) -> str:
    """Search the web for information."""
    # Implementation
    return f"Web results for: {query}"

tools = [
    Tool(
        name="DatabaseSearch",
        func=search_database,
        description="Useful for searching internal database. Input should be a search query."
    ),
    Tool(
        name="WebSearch",
        func=web_search,
        description="Useful for searching the web for current information. Input should be a search query."
    )
]

# Create prompt
prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# Create agent
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

# Add memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

# Run agent
result = agent_executor.invoke({
    "input": "What are the latest sales figures and industry trends?"
})

print(result['output'])
```

---

## LangGraph for Complex Workflows

### State-Based Agent Architecture

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    data: dict
    iterations: int
    max_iterations: int

# Define nodes (agent functions)
def researcher(state: AgentState) -> AgentState:
    """Research information on a topic."""
    messages = state['messages']
    question = messages[-1].content
    
    # Use research tools
    research_result = research_agent.invoke(question)
    
    return {
        **state,
        "messages": [AIMessage(content=research_result)],
        "data": {**state.get('data', {}), "research": research_result},
        "iterations": state.get('iterations', 0) + 1
    }

def analyzer(state: AgentState) -> AgentState:
    """Analyze researched information."""
    research_data = state['data'].get('research', '')
    
    # Analyze data
    analysis = analyzer_agent.invoke(research_data)
    
    return {
        **state,
        "messages": [AIMessage(content=analysis)],
        "data": {**state['data'], "analysis": analysis},
        "iterations": state.get('iterations', 0) + 1
    }

def writer(state: AgentState) -> AgentState:
    """Write final report based on analysis."""
    analysis = state['data'].get('analysis', '')
    
    # Generate report
    report = writer_agent.invoke(analysis)
    
    return {
        **state,
        "messages": [AIMessage(content=report)],
        "data": {**state['data'], "report": report},
        "iterations": state.get('iterations', 0) + 1
    }

# Define routing logic
def should_continue(state: AgentState) -> str:
    """Determine next step based on state."""
    
    if state['iterations'] >= state['max_iterations']:
        return "end"
    
    current_step = state.get('current_step', 'research')
    
    if current_step == 'research':
        return "analyze"
    elif current_step == 'analyze':
        # Check if analysis is satisfactory
        if "needs more research" in state['data'].get('analysis', '').lower():
            return "research"
        return "write"
    elif current_step == 'write':
        return "end"
    
    return "end"

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("research", researcher)
workflow.add_node("analyze", analyzer)
workflow.add_node("write", writer)

# Set entry point
workflow.set_entry_point("research")

# Add edges
workflow.add_conditional_edges(
    "research",
    should_continue,
    {
        "analyze": "analyze",
        "end": END
    }
)

workflow.add_conditional_edges(
    "analyze",
    should_continue,
    {
        "research": "research",
        "write": "write",
        "end": END
    }
)

workflow.add_conditional_edges(
    "write",
    should_continue,
    {
        "end": END
    }
)

# Compile graph
app = workflow.compile()

# Run workflow
result = app.invoke({
    "messages": [HumanMessage(content="Write a report on AI trends in 2024")],
    "current_step": "research",
    "data": {},
    "iterations": 0,
    "max_iterations": 10
})

print(result['data']['report'])
```

### Multi-Agent Collaboration

```python
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph

class MultiAgentSystem:
    
    def __init__(self):
        self.llm = Bedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # Create specialized agents
        self.data_analyst = self.create_data_agent()
        self.researcher = self.create_research_agent()
        self.writer = self.create_writer_agent()
        self.supervisor = self.create_supervisor_agent()
    
    def create_data_agent(self):
        """Agent specialized in data analysis."""
        tools = [
            Tool(
                name="QueryDatabase",
                func=self.query_database,
                description="Query SQL database for data"
            ),
            Tool(
                name="AnalyzeData",
                func=self.analyze_data,
                description="Perform statistical analysis on data"
            )
        ]
        
        return create_react_agent(
            model=self.llm,
            tools=tools,
            state_modifier="You are a data analyst expert."
        )
    
    def create_research_agent(self):
        """Agent specialized in research."""
        tools = [
            Tool(
                name="WebSearch",
                func=self.web_search,
                description="Search the web for information"
            ),
            Tool(
                name="ReadPaper",
                func=self.read_paper,
                description="Read and summarize research papers"
            )
        ]
        
        return create_react_agent(
            model=self.llm,
            tools=tools,
            state_modifier="You are a research expert."
        )
    
    def create_writer_agent(self):
        """Agent specialized in writing."""
        tools = [
            Tool(
                name="WriteSection",
                func=self.write_section,
                description="Write a section of the report"
            ),
            Tool(
                name="EditText",
                func=self.edit_text,
                description="Edit and improve text"
            )
        ]
        
        return create_react_agent(
            model=self.llm,
            tools=tools,
            state_modifier="You are a professional writer."
        )
    
    def create_supervisor_agent(self):
        """Supervisor agent that coordinates other agents."""
        
        prompt = """You are a supervisor managing a team of AI agents:
        - data_analyst: Queries and analyzes data
        - researcher: Searches for information and research
        - writer: Writes reports and documents
        
        Given the user request, decide which agent should act next.
        When the task is complete, respond with FINISH.
        
        Request: {input}
        
        Which agent should act next?"""
        
        return self.llm

    def run(self, task: str):
        """Run the multi-agent system."""
        
        state = {
            "task": task,
            "results": {},
            "messages": [],
            "next_agent": None
        }
        
        max_iterations = 10
        for i in range(max_iterations):
            # Supervisor decides next agent
            decision = self.supervisor.invoke({
                "input": task,
                "results": state['results']
            })
            
            if "FINISH" in decision:
                break
            
            # Route to appropriate agent
            if "data_analyst" in decision.lower():
                result = self.data_analyst.invoke({"input": task})
                state['results']['data_analysis'] = result
            elif "researcher" in decision.lower():
                result = self.researcher.invoke({"input": task})
                state['results']['research'] = result
            elif "writer" in decision.lower():
                result = self.writer.invoke({"input": task})
                state['results']['report'] = result
        
        return state['results']

# Usage
system = MultiAgentSystem()
result = system.run("Create a market analysis report for Q4 2024")
```

---

## MCP (Model Context Protocol) Integration

### What is MCP?

MCP is a standardized protocol for connecting AI models to external tools, data sources, and services.

### MCP Server Implementation

```python
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import asyncio
import boto3

# Create MCP server
server = Server("database-mcp-server")

# AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
rds = boto3.client('rds-data')

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="query_dynamodb",
            description="Query DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "key": {"type": "object"}
                },
                "required": ["table_name", "key"]
            }
        ),
        Tool(
            name="read_s3_file",
            description="Read file from S3",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket": {"type": "string"},
                    "key": {"type": "string"}
                },
                "required": ["bucket", "key"]
            }
        ),
        Tool(
            name="execute_sql",
            description="Execute SQL query on RDS",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "database": {"type": "string"}
                },
                "required": ["query", "database"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "query_dynamodb":
        table = dynamodb.Table(arguments['table_name'])
        response = table.get_item(Key=arguments['key'])
        item = response.get('Item', {})
        
        return [TextContent(
            type="text",
            text=json.dumps(item, default=str)
        )]
    
    elif name == "read_s3_file":
        obj = s3.get_object(
            Bucket=arguments['bucket'],
            Key=arguments['key']
        )
        content = obj['Body'].read().decode('utf-8')
        
        return [TextContent(
            type="text",
            text=content
        )]
    
    elif name == "execute_sql":
        response = rds.execute_statement(
            sql=arguments['query'],
            database=arguments['database'],
            resourceArn=os.environ['RDS_ARN'],
            secretArn=os.environ['RDS_SECRET_ARN']
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(response['records'], default=str)
        )]
    
    return [TextContent(type="text", text="Unknown tool")]

# Run server
async def main():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="database-mcp-server",
                server_version="1.0.0"
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### MCP Client Usage in LangChain

```python
from langchain.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

class MCPToolWrapper:
    """Wrapper for MCP tools to use in LangChain."""
    
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session = None
    
    async def connect(self):
        """Connect to MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path]
        )
        
        stdio_transport = await stdio_client(server_params)
        self.session = ClientSession(
            stdio_transport.read,
            stdio_transport.write
        )
        
        await self.session.initialize()
    
    async def list_tools(self):
        """Get available tools from MCP server."""
        response = await self.session.list_tools()
        return response.tools
    
    async def call_tool(self, name: str, arguments: dict):
        """Call tool via MCP."""
        response = await self.session.call_tool(name, arguments)
        return response.content[0].text
    
    def to_langchain_tools(self) -> list:
        """Convert MCP tools to LangChain tools."""
        
        async def _list_tools():
            if not self.session:
                await self.connect()
            return await self.list_tools()
        
        mcp_tools = asyncio.run(_list_tools())
        
        langchain_tools = []
        for mcp_tool in mcp_tools:
            
            def make_tool_func(tool_name):
                async def tool_func(**kwargs):
                    return await self.call_tool(tool_name, kwargs)
                return lambda **kwargs: asyncio.run(tool_func(**kwargs))
            
            tool = StructuredTool(
                name=mcp_tool.name,
                description=mcp_tool.description,
                func=make_tool_func(mcp_tool.name),
                args_schema=mcp_tool.inputSchema
            )
            langchain_tools.append(tool)
        
        return langchain_tools

# Usage
mcp_wrapper = MCPToolWrapper("./database_mcp_server.py")
mcp_tools = mcp_wrapper.to_langchain_tools()

# Create agent with MCP tools
agent = create_react_agent(
    model=llm,
    tools=mcp_tools
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=mcp_tools,
    verbose=True
)

result = agent_executor.invoke({
    "input": "Query the customers table for user ID 123"
})
```

---

## LangSmith for Monitoring

### Setup & Configuration

```python
import os
from langsmith import Client
from langsmith.run_helpers import traceable

# Configure LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "production-agents"

client = Client()

# Decorate functions for tracing
@traceable(name="research_task", run_type="chain")
def research_task(query: str) -> str:
    """Traced research function."""
    
    # Your logic here
    result = research_agent.invoke(query)
    
    return result

@traceable(name="analyze_data", run_type="tool")
def analyze_data(data: str) -> dict:
    """Traced analysis function."""
    
    # Analysis logic
    analysis = perform_analysis(data)
    
    return analysis

# Use in agent
result = research_task("AI trends 2024")
analysis = analyze_data(result)
```

### Custom Logging & Metrics

```python
from langsmith import Client
from datetime import datetime

client = Client()

class TrackedAgent:
    
    def __init__(self, agent_executor, project_name: str):
        self.agent_executor = agent_executor
        self.project_name = project_name
        self.client = Client()
    
    def invoke(self, input_data: dict):
        """Invoke agent with full tracking."""
        
        run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Run agent
            result = self.agent_executor.invoke(input_data)
            
            # Log success
            self.client.create_run(
                name="agent_execution",
                run_type="chain",
                inputs=input_data,
                outputs=result,
                start_time=start_time,
                end_time=datetime.now(),
                project_name=self.project_name,
                tags=["production", "success"]
            )
            
            return result
            
        except Exception as e:
            # Log error
            self.client.create_run(
                name="agent_execution",
                run_type="chain",
                inputs=input_data,
                error=str(e),
                start_time=start_time,
                end_time=datetime.now(),
                project_name=self.project_name,
                tags=["production", "error"]
            )
            
            raise
    
    def get_metrics(self, days: int = 7):
        """Get agent performance metrics."""
        
        runs = self.client.list_runs(
            project_name=self.project_name,
            start_time=datetime.now() - timedelta(days=days)
        )
        
        metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_latency": 0,
            "total_tokens": 0
        }
        
        latencies = []
        for run in runs:
            metrics["total_runs"] += 1
            
            if run.error:
                metrics["failed_runs"] += 1
            else:
                metrics["successful_runs"] += 1
            
            if run.end_time and run.start_time:
                latency = (run.end_time - run.start_time).total_seconds()
                latencies.append(latency)
            
            if run.outputs:
                metrics["total_tokens"] += run.outputs.get("token_usage", {}).get("total_tokens", 0)
        
        if latencies:
            metrics["avg_latency"] = sum(latencies) / len(latencies)
        
        return metrics

# Usage
tracked_agent = TrackedAgent(agent_executor, "production-agents")
result = tracked_agent.invoke({"input": "Analyze Q4 sales"})
metrics = tracked_agent.get_metrics(days=30)
print(metrics)
```

### A/B Testing with LangSmith

```python
from langsmith import Client
import random

class ABTestingAgent:
    
    def __init__(self, agent_a, agent_b, split_ratio: float = 0.5):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.split_ratio = split_ratio
        self.client = Client()
    
    def invoke(self, input_data: dict):
        """Route to agent A or B based on split ratio."""
        
        use_agent_a = random.random() < self.split_ratio
        variant = "A" if use_agent_a else "B"
        agent = self.agent_a if use_agent_a else self.agent_b
        
        with self.client.trace(
            name="ab_test_execution",
            metadata={"variant": variant}
        ) as run:
            result = agent.invoke(input_data)
            run.end(outputs=result)
        
        return result
    
    def analyze_variants(self, days: int = 7):
        """Compare performance of variants."""
        
        runs = self.client.list_runs(
            project_name="ab-testing",
            start_time=datetime.now() - timedelta(days=days)
        )
        
        variant_a_metrics = {"latencies": [], "successes": 0, "failures": 0}
        variant_b_metrics = {"latencies": [], "successes": 0, "failures": 0}
        
        for run in runs:
            variant = run.extra.get("metadata", {}).get("variant")
            
            if variant == "A":
                metrics = variant_a_metrics
            elif variant == "B":
                metrics = variant_b_metrics
            else:
                continue
            
            if run.error:
                metrics["failures"] += 1
            else:
                metrics["successes"] += 1
            
            if run.end_time and run.start_time:
                latency = (run.end_time - run.start_time).total_seconds()
                metrics["latencies"].append(latency)
        
        return {
            "variant_a": {
                "success_rate": variant_a_metrics["successes"] / 
                    (variant_a_metrics["successes"] + variant_a_metrics["failures"]),
                "avg_latency": sum(variant_a_metrics["latencies"]) / len(variant_a_metrics["latencies"])
                    if variant_a_metrics["latencies"] else 0
            },
            "variant_b": {
                "success_rate": variant_b_metrics["successes"] / 
                    (variant_b_metrics["successes"] + variant_b_metrics["failures"]),
                "avg_latency": sum(variant_b_metrics["latencies"]) / len(variant_b_metrics["latencies"])
                    if variant_b_metrics["latencies"] else 0
            }
        }
```

---

## Production Architecture

### Complete Agentic System

```python
from langgraph.graph import StateGraph, END
from langchain_community.llms import Bedrock
from langchain.agents import AgentExecutor
from langsmith import Client
import boto3

class ProductionAgentSystem:
    
    def __init__(self):
        # Initialize LLM
        self.llm = Bedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"max_tokens": 4096}
        )
        
        # Initialize MCP tools
        self.mcp_tools = self.setup_mcp_tools()
        
        # Initialize agents
        self.planner = self.create_planner_agent()
        self.executor = self.create_executor_agent()
        self.reviewer = self.create_reviewer_agent()
        
        # Initialize monitoring
        self.langsmith_client = Client()
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "production-system"
        
        # Build workflow
        self.workflow = self.build_workflow()
    
    def setup_mcp_tools(self):
        """Setup MCP server connections."""
        mcp_servers = [
            MCPToolWrapper("./database_server.py"),
            MCPToolWrapper("./aws_server.py"),
            MCPToolWrapper("./web_search_server.py")
        ]
        
        all_tools = []
        for server in mcp_servers:
            all_tools.extend(server.to_langchain_tools())
        
        return all_tools
    
    def create_planner_agent(self):
        """Create planning agent."""
        prompt = """You are a planning agent. Break down the user's request into clear, actionable steps.
        
        Available tools: {tools}
        
        User request: {input}
        
        Create a plan:"""
        
        return create_react_agent(
            model=self.llm,
            tools=self.mcp_tools,
            state_modifier=prompt
        )
    
    def create_executor_agent(self):
        """Create execution agent."""
        return create_react_agent(
            model=self.llm,
            tools=self.mcp_tools,
            state_modifier="You are an execution agent. Follow the plan and use tools to accomplish tasks."
        )
    
    def create_reviewer_agent(self):
        """Create review agent."""
        return create_react_agent(
            model=self.llm,
            tools=[],  # Review agent doesn't use tools
            state_modifier="You are a review agent. Verify that results meet requirements."
        )
    
    def build_workflow(self):
        """Build LangGraph workflow."""
        
        workflow = StateGraph(AgentState)
        
        workflow.add_node("plan", self.plan_node)
        workflow.add_node("execute", self.execute_node)
        workflow.add_node("review", self.review_node)
        
        workflow.set_entry_point("plan")
        
        workflow.add_edge("plan", "execute")
        workflow.add_conditional_edges(
            "execute",
            self.should_review,
            {
                "review": "review",
                "end": END
            }
        )
        workflow.add_conditional_edges(
            "review",
            self.review_decision,
            {
                "execute": "execute",
                "end": END
            }
        )
        
        return workflow.compile()
    
    @traceable(name="plan_node")
    def plan_node(self, state: AgentState) -> AgentState:
        """Planning node."""
        result = self.planner.invoke(state)
        return {**state, "plan": result, "current_step": "execute"}
    
    @traceable(name="execute_node")
    def execute_node(self, state: AgentState) -> AgentState:
        """Execution node."""
        result = self.executor.invoke(state)
        return {**state, "execution_result": result, "current_step": "review"}
    
    @traceable(name="review_node")
    def review_node(self, state: AgentState) -> AgentState:
        """Review node."""
        result = self.reviewer.invoke(state)
        return {**state, "review_result": result}
    
    def should_review(self, state: AgentState) -> str:
        """Decide if review is needed."""
        if state.get("skip_review"):
            return "end"
        return "review"
    
    def review_decision(self, state: AgentState) -> str:
        """Decide next step based on review."""
        review = state.get("review_result", {})
        
        if "approved" in str(review).lower():
            return "end"
        elif state.get("iterations", 0) > 3:
            return "end"  # Max retries
        else:
            return "execute"
    
    def invoke(self, user_input: str, **kwargs):
        """Main entry point."""
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "current_step": "plan",
            "iterations": 0,
            "max_iterations": 5,
            **kwargs
        }
        
        try:
            result = self.workflow.invoke(initial_state)
            
            # Log metrics
            self.log_execution_metrics(result)
            
            return result
            
        except Exception as e:
            # Log error
            self.langsmith_client.create_run(
                name="agent_error",
                run_type="chain",
                inputs={"user_input": user_input},
                error=str(e),
                project_name="production-system",
                tags=["error"]
            )
            raise
    
    def log_execution_metrics(self, result: dict):
        """Log execution metrics to CloudWatch."""
        
        cloudwatch = boto3.client('cloudwatch')
        
        cloudwatch.put_metric_data(
            Namespace='AgentSystem',
            MetricData=[
                {
                    'MetricName': 'ExecutionSuccess',
                    'Value': 1 if result.get('execution_result') else 0,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'Iterations',
                    'Value': result.get('iterations', 0),
                    'Unit': 'Count'
                }
            ]
        )

# Usage
system = ProductionAgentSystem()
result = system.invoke("Analyze customer churn and create a report")
```

---

## AWS Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  API Gateway (REST/WebSocket)                                │
│  - Authentication (Cognito)                                  │
│  - Rate limiting                                             │
│  - Request validation                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ALB → ECS Fargate (Agent Application)                       │
│  - Auto-scaling                                              │
│  - Health checks                                             │
│  - Container insights                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Layer                                                 │
│  - LangGraph workflows                                       │
│  - LangChain agents                                          │
│  - MCP tool integration                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────┬──────────────────┬─────────────────────┐
│  LLM Services    │  Data Layer      │  Tool Layer          │
│  - Bedrock       │  - DynamoDB      │  - Lambda functions  │
│  - OpenAI        │  - RDS           │  - Step Functions    │
│                  │  - S3            │  - External APIs     │
│                  │  - ElastiCache   │                      │
└──────────────────┴──────────────────┴─────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Monitoring & Observability                                  │
│  - LangSmith (traces)                                        │
│  - CloudWatch (metrics, logs)                                │
│  - X-Ray (distributed tracing)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Agent Design
- ✅ Single responsibility per agent
- ✅ Clear tool descriptions
- ✅ Handle errors gracefully
- ✅ Set max iterations
- ✅ Implement timeouts
- ✅ Use typed state for LangGraph
- ✅ Validate tool inputs/outputs

### 2. Performance
- ✅ Cache LLM responses when appropriate
- ✅ Use streaming for long responses
- ✅ Implement parallel tool calls
- ✅ Optimize prompt length
- ✅ Batch operations where possible
- ✅ Use read replicas for databases

### 3. Monitoring
- ✅ Enable LangSmith tracing
- ✅ Track token usage
- ✅ Monitor latency
- ✅ Log all decisions
- ✅ Implement health checks
- ✅ Set up alerts

### 4. Security
- ✅ Validate all inputs
- ✅ Use IAM roles (no hardcoded credentials)
- ✅ Implement rate limiting
- ✅ Audit tool usage
- ✅ Encrypt sensitive data
- ✅ Use VPC for private resources

### 5. Cost Optimization
- ✅ Cache frequent queries
- ✅ Use smaller models where possible
- ✅ Implement token limits
- ✅ Monitor API costs
- ✅ Use reserved capacity when available

---

## Common Use Cases

1. **Research Assistant**: Multi-step research with web search and summarization
2. **Code Assistant**: Code generation, review, and debugging
3. **Data Analyst**: Query databases, analyze data, create reports
4. **Customer Support**: Answer questions, create tickets, route issues
5. **Content Generator**: Research topics, write articles, generate images
6. **Workflow Automation**: Multi-step business processes
7. **Personal Assistant**: Schedule meetings, send emails, manage tasks

---

This comprehensive design provides everything needed to build production-grade agentic AI systems!
