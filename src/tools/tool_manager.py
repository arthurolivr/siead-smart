class ToolManager:
    def __init__(self):
        self.tools = {}

    def register_tool(self, name, tool_instance):
        self.tools[name] = tool_instance

    def run_tool(self, name, *args, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool {name} não registrada")

        tool = self.tools[name]
        return tool.run(*args, **kwargs)