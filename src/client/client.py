import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.messages import MessageHandler
from fastmcp.client import Client
import mcp.types
from fastmcp.client.logging import LogMessage
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a logger for the module where the client is used
logger = logging.getLogger(__name__)

# This mapping is useful for converting MCP level strings to Python's levels
LOGGING_LEVEL_MAP = logging.getLevelNamesMapping()


class ToolCacheHandler(MessageHandler):
    def __init__(self):
        self.cached_tools = []
    
    async def on_tool_list_changed(
        self, notification: mcp.types.ToolListChangedNotification
    ) -> None:
        """Clear tool cache when tools change."""
        print("Tools changed - clearing cache")
        print(notification)
        self.cached_tools = []  # Force refresh on next access
        
        
async def log_handler(message: LogMessage):
    """
    Handles incoming logs from the MCP server and forwards them
    to the standard Python logging system.
    """
    msg = message.data.get('msg')
    extra = message.data.get('extra')

    # Convert the MCP log level to a Python log level
    level = LOGGING_LEVEL_MAP.get(message.level.upper(), logging.INFO)

    # Log the message using the standard logging library
    logger.log(level, msg, extra=extra)
        
# Custom progress handler with enhanced output formatting
async def my_progress_handler(
    progress: float, 
    total: float | None, 
    message: str | None
) -> None:
    if total is not None:
        percentage = (progress / total) * 100
        print(f"[Progress] {percentage:.1f}% complete — {message or 'No message provided'}")
        if progress == 2:
            print("Halfway there!, should I notify someone?")
    else:
        print(f"[Progress] {progress} units — {message or 'No message provided'}")

async def main():
    print("[Setup] Initializing transport and client...")

    # Set up the transport (removed Authorization header if not needed)
    transport = StreamableHttpTransport(
        url="http://localhost:8000/mcp",
        headers={
            "Authorization": "Bearer your-token-here",
            "X-Custom-Header": "value"
        }
    )

    # Initialize the client
    client = Client(transport=transport, message_handler=ToolCacheHandler(),  log_handler=log_handler,)

    try:
        async with client:
            print("[Client] Connected successfully.")
            tools = await client.list_tools()
            
            print("----- Available Tools -------")
            available_tools = {}
            for tool in tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")
                if tool.inputSchema:
                    print(f"Parameters: {tool.inputSchema}")
                # Access tags and other metadata
                if hasattr(tool, 'meta') and tool.meta:
                    fastmcp_meta = tool.meta.get('_fastmcp', {})
                    print(f"Tags: {fastmcp_meta.get('tags', [])}")
                print("------------------")
                available_tools[tool.name] = tool
            
            # Dynamically call tools based on availability
            if "hello" in available_tools:
                print("[Tool Call] Invoking 'hello' tool with name='Alice'...")
                try:
                    result = await client.call_tool("hello", {"name": "Alice"})
                    print(f"[Result] Hello Tool Response: {result}")
                except Exception as e:
                    print(f"[Error] Failed to call 'hello' tool: {e}")
            else:
                print("[Info] 'hello' tool not available because it's disabled")
            
            if "fruit_processor" in available_tools:
                fruits = ["apple", "banana", "cherry"]
                print(f"[Tool Call] Invoking 'fruit_processor' tool with fruit={fruits}...")
                try:
                    result = await client.call_tool(
                        "fruit_processor", 
                        {"fruits": fruits}, 
                        progress_handler=my_progress_handler
                    )
                    print(f"[Result] fruit_processor Response: {result.structured_content}")
                except Exception as e:
                    print(f"[Error] Failed to call 'fruit_processor' tool: {e}")
            else:
                print("[Info] 'fruit_processor' tool not available")
                                    
    except Exception as e:
        print(f"[Error] Client operation failed: {e}")

def run():
    """Synchronous wrapper for the async main function."""
    asyncio.run(main())

if __name__ == "__main__":
    print("[Main] Starting async client...")
    run()