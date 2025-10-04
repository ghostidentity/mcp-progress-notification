import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client import Client

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

    # Set up the transport with custom headers for authentication
    transport = StreamableHttpTransport(
        url="http://localhost:8000/mcp",
        headers={
            "Authorization": "Bearer your-token-here",
            "X-Custom-Header": "value"
        }
    )

    # Initialize the client
    client = Client(transport=transport)

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
                print("[Info] 'hello' tool not available")
            
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

if __name__ == "__main__":
    print("[Main] Starting async client...")
    asyncio.run(main())