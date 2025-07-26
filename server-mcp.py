from mcp.server.fastmcp import FastMCP

app = FastMCP(name="INFO API", instructions="""
    This is a simple API to search for information.
    You can use the `infoApi` tool to search for information.
""")

@app.tool()
def infoApi(name: str) -> str:
    """
    This tool searches for information api by namÇe.
    args:
        name: The name of the information api to search for.
    returns:
        String with information api.
    """
    return "essa api é responsavel por dar dados de extratos bancários, faturas de cartão de crédito, etc."

if __name__ == '__main__':
    app.run(transport='streamable-http')