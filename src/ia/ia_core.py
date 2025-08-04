from src.tools.tool_manager import ToolManager
from src.tools.example_tool import ExampleTool
from src.utils.excel_logger import ExcelLogger

class IA:
    def __init__(self):
        self.tool_manager = ToolManager()
        self.excel_logger = ExcelLogger("interactions.xlsx")
        self.tool_manager.register_tool("example", ExampleTool())

    def ask(self, question, tool_name):
        self.excel_logger.log_question(question)
        result = self.tool_manager.run_tool(tool_name)
        return result