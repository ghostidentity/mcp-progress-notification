import asyncio
from fastmcp import Context, FastMCP

mcp = FastMCP("MyServer")

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
    
    # Report 100% completion
    await ctx.report_progress(progress=total, total=total)
    
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