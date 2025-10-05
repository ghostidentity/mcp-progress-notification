import asyncio
from fastmcp import Context, FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        
        print("The tool has been executed")
        tool_name = context.message.name
        tool = await context.fastmcp_context.fastmcp.get_tool(tool_name)
        
        print("---------------------")
        print(f"Tool details: {tool}")
        print("---------------------")

        # Middleware stores user info in context state
        context.fastmcp_context.set_state("user_id", "user_123")
        context.fastmcp_context.set_state("permissions", ["read", "write"])
        
        if "test" in tool.tags:
            #raise ToolError(f"Access denied to test tool: {tool_name}")
            pass

        print(f"-> Received {context.method}")
        result = await call_next(context)
        print(f"<- Responded to {context.method}")
        
        return result
    
mcp = FastMCP("MyServer")
mcp.add_middleware(LoggingMiddleware())


@mcp.tool(
    name="fruit_processor",        
    description="tool to process items with progress updates",
    tags={"test"},   
    meta={"version": "1.2", "author": "Mark"},
    enabled=True
)
async def fruit_processor(fruits: list[str], ctx: Context) -> dict:
    """Process a list of items with progress updates."""
    total = len(fruits)
    processed_items = []
    unprocessed_items = []
    
    user_id = ctx.get_state("user_id")  # "user_123"
    
    print(f"User ID from context state: {user_id}")
    
    ctx.set_state("user_id", "user_124")
    #the next tool call will still user_123 as user_id, because the ctx.set_state is session to the current tool call only.
    
    for i, item in enumerate(fruits):
        # Report progress as we process each item
        await ctx.report_progress(progress=i, total=total, message=f"Processing fruit {i+1} of {total}")
        await asyncio.sleep(5)
        
        print("processing", item)
        if item != "banana":
            print("processed", item)
            processed_items.append(item.upper())
        else:
            print("skipped", item)
            unprocessed_items.append(item.upper())
            await ctx.info("Banana is not allowed", extra={
            "sequence": i
        })
    
    # Report 100% completion
    await ctx.report_progress(progress=total, total=total)
    await ctx.send_tool_list_changed() # Notify clients of potential tool changes  (Demo purpose)
    
    #mcp.add_tools_from_modules(["src.server.tools"])  # Dynamically add tools (Demo purpose)
    
    return {
        "processed": processed_items,
        "unprocessed": unprocessed_items
    }

@mcp.tool(
    name="hello",        
    description="just a simple hello",
    tags={"test"},   
    meta={"version": "1.2", "author": "Mark"},
    enabled=False
)
def hello(name: str) -> str:
    return f"Hello, {name}!"

def main():
    # Start an HTTP server on port 8000
    mcp.run(transport="streamable-http", host="localhost", port=8000)

if __name__ == "__main__":
    main()