from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class AppendSharedStorageInput(BaseModel):
    data: str = Field(..., description="The content (passwords, flags, open ports, sensitive findings) to append to the shared storage.")

class AppendSharedStorageTool(BaseTool):
    name: str = "append_to_shared_storage"
    description: str = "Appends important findings (passwords, flags, open ports, etc.) to the shared storage file for other agents to read."
    args_schema: Type[BaseModel] = AppendSharedStorageInput
    storage_path: str = ""

    def _run(self, data: str) -> str:
        if not self.storage_path:
            return "Error: Storage path not configured."
        try:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(f"\n{data}\n")
            return f"Successfully appended data to shared storage."
        except Exception as e:
            return f"Error appending to shared storage: {str(e)}"

class ReadSharedStorageTool(BaseTool):
    name: str = "read_shared_storage"
    description: str = "Reads the contents of the shared storage file to see what other agents have discovered so far."
    storage_path: str = ""

    def _run(self) -> str:
        if not self.storage_path:
            return "Error: Storage path not configured."
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                return "The shared storage file is currently empty."
            return content
        except FileNotFoundError:
            return "The shared storage file does not exist yet or is empty."
        except Exception as e:
            return f"Error reading shared storage: {str(e)}"
