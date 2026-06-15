#!/usr/bin/env python3
"""
Claude Code with Local Memory System.
This implementation provides persistent memory storage using the file system,
working seamlessly with LM Studio or any Anthropic-compatible API.
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic

# Initialize Claude client
anthropic = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY", "sk-lm-sExJDMeq:95TtIegpbxZm20KsVvai")
)

# Memory storage directory
MEMORY_DIR = Path(__file__).parent / "memories"


class LocalMemoryStore:
    """Local file-based memory storage system for Claude interactions."""

    def __init__(self, memory_dir: str = None):
        self.memory_dir = Path(memory_dir) if memory_dir else MEMORY_DIR
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def save_memory(self, key: str, content: str, category: str = "general") -> dict:
        """Save a memory entry."""
        timestamp = datetime.now().isoformat()

        # Create category directory if needed
        category_dir = self.memory_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Create memory file with timestamp
        filename = f"{key}_{timestamp.replace(':', '-')}.json"
        filepath = category_dir / filename

        memory_entry = {
            "id": f"mem_{key}_{timestamp}",
            "key": key,
            "content": content,
            "category": category,
            "created_at": timestamp,
            "updated_at": timestamp
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory_entry, f, ensure_ascii=False, indent=2)

        print(f"💾 Memory saved: {key} (category: {category})")
        return memory_entry

    def get_memories(self, key: str = None, category: str = None) -> list:
        """Retrieve memories by key or category."""
        memories = []

        search_dirs = [self.memory_dir]
        if category:
            search_dirs = [self.memory_dir / category]

        for dir_path in search_dirs:
            if not dir_path.exists():
                continue

            pattern = str(dir_path / "*.json")
            for filepath in glob.glob(pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        memory = json.load(f)

                    if key and memory.get("key") != key:
                        continue

                    memories.append(memory)
                except (json.JSONDecodeError, IOError):
                    continue

        # Sort by creation time (newest first)
        memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return memories

    def get_memory_context(self, key: str = None, category: str = None, max_memories: int = 5) -> str:
        """Get formatted memory context for Claude prompts."""
        memories = self.get_memories(key, category)[:max_memories]

        if not memories:
            return ""

        context_parts = ["\n## Previous Memories (for context):\n"]
        for i, memory in enumerate(memories, 1):
            context_parts.append(
                f"{i}. **[{memory.get('category', 'general')}]** "
                f"({memory.get('created_at', '')[:10]}): {memory['content']}"
            )

        return "\n".join(context_parts) + "\n"

    def delete_memory(self, key: str = None, category: str = None) -> int:
        """Delete memories matching the criteria."""
        deleted_count = 0

        search_dirs = [self.memory_dir]
        if category:
            search_dirs = [self.memory_dir / category]

        for dir_path in search_dirs:
            if not dir_path.exists():
                continue

            pattern = str(dir_path / "*.json")
            for filepath in glob.glob(pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        memory = json.load(f)

                    if key and memory.get("key") != key:
                        continue

                    os.remove(filepath)
                    deleted_count += 1
                except (json.JSONDecodeError, IOError):
                    continue

        print(f"🗑️ Deleted {deleted_count} memory(ies)")
        return deleted_count

    def list_categories(self) -> list:
        """List all memory categories."""
        categories = []
        for item in self.memory_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories.append(item.name)
        return sorted(categories)

    def get_stats(self) -> dict:
        """Get memory storage statistics."""
        stats = {
            "total_memories": 0,
            "categories": {},
            "storage_path": str(self.memory_dir)
        }

        for category in self.list_categories():
            cat_path = self.memory_dir / category
            memories = list(cat_path.glob("*.json"))
            stats["categories"][category] = len(memories)
            stats["total_memories"] += len(memories)

        return stats


def claude_with_memory(prompt: str, context: str = "", memory_key: str = None,
                       category: str = "general", save_response: bool = True) -> str:
    """
    Use Claude with local memory capabilities.

    This function integrates Claude API calls with a file-based memory system,
    allowing persistent context across sessions.

    Args:
        prompt (str): The user's prompt/question
        context (str): Additional context to provide
        memory_key (str, optional): Key to retrieve specific memories
        category (str, optional): Memory category (default: "general")
        save_response (bool, optional): Whether to save Claude's response as memory

    Returns:
        str: Claude's response with memory awareness
    """
    # Initialize memory store
    memory_store = LocalMemoryStore()

    # Retrieve relevant memories
    memory_context = memory_store.get_memory_context(memory_key, category)

    # Build enhanced prompt with memories
    if memory_context:
        print(f"📚 Loaded {len(memory_store.get_memories(memory_key, category))} memory(ies)")
        enhanced_prompt = f"{memory_context}\n{prompt}"
    else:
        print("🆕 No previous memories found")
        enhanced_prompt = prompt

    if context:
        enhanced_prompt += f"\n\nAdditional Context: {context}"

    # Get Claude's response
    try:
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

        response = anthropic.messages.create(
            model=model,
            max_tokens=2048,
            messages=[
                {"role": "user", "content": enhanced_prompt}
            ]
        )

        result = response.content[0].text

        # Save response as memory if requested
        if save_response and memory_key:
            memory_store.save_memory(
                key=memory_key,
                content=f"Q: {prompt}\nA: {result}",
                category=category
            )

        print(f"✨ Claude's response:\n{result}")
        return result

    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return f"Error occurred while processing the request. Details: {str(e)}"


def demo_memory_system():
    """Demonstrate the local memory system."""
    print("=" * 60)
    print("🧠 Claude Code with Local Memory System")
    print("=" * 60)

    memory_store = LocalMemoryStore()

    # Show current stats
    print("\n📊 Current Memory Stats:")
    stats = memory_store.get_stats()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Categories: {', '.join(stats['categories'].keys()) if stats['categories'] else 'None'}")
    print(f"   Storage path: {stats['storage_path']}")

    # Demo 1: Save a memory
    print("\n" + "=" * 60)
    print("📝 Demo 1: Saving a memory")
    print("=" * 60)
    memory_store.save_memory(
        key="user_preferences",
        content="User prefers Python projects with clean architecture and comprehensive testing.",
        category="user_profile"
    )

    # Demo 2: Retrieve memories
    print("\n" + "=" * 60)
    print("📖 Demo 2: Retrieving memories")
    print("=" * 60)
    memories = memory_store.get_memories(category="user_profile")
    for i, mem in enumerate(memories, 1):
        print(f"   {i}. [{mem['category']}] ({mem['created_at'][:10]}): {mem['content']}")

    # Demo 3: List categories
    print("\n" + "=" * 60)
    print("📁 Demo 3: Memory Categories")
    print("=" * 60)
    categories = memory_store.list_categories()
    for cat in categories:
        count = len(list((memory_store.memory_dir / cat).glob("*.json")))
        print(f"   • {cat}: {count} memory(ies)")

    # Demo 4: Interactive mode
    print("\n" + "=" * 60)
    print("💬 Demo 4: Interactive Memory Mode")
    print("=" * 60)
    print("Type 'save <key> <content>' to save a memory")
    print("Type 'get <key>' or 'get category:<category>' to retrieve memories")
    print("Type 'list' to see all categories")
    print("Type 'stats' for storage statistics")
    print("Type 'clear <key>' or 'clear category:<category>' to delete memories")
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("🧠 Memory> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("\n👋 Goodbye!")
                break

            parts = user_input.split(None, 2)
            command = parts[0].lower()

            if command == 'save' and len(parts) >= 3:
                key = parts[1]
                content = parts[2]
                memory_store.save_memory(key, content)

            elif command == 'get':
                if ':' in parts[1]:
                    category = parts[1].split(':')[1]
                    memories = memory_store.get_memories(category=category)
                else:
                    key = parts[1]
                    memories = memory_store.get_memories(key=key)

                if memories:
                    print(f"\n📚 Found {len(memories)} memory(ies):")
                    for i, mem in enumerate(memories, 1):
                        print(f"   {i}. [{mem['category']}] ({mem['created_at'][:10]}):")
                        print(f"      {mem['content']}")
                else:
                    print("   No memories found.")

            elif command == 'list':
                categories = memory_store.list_categories()
                if categories:
                    print(f"\n📁 Categories ({len(categories)}):")
                    for cat in categories:
                        count = len(list((memory_store.memory_dir / cat).glob("*.json")))
                        print(f"   • {cat}: {count} memory(ies)")
                else:
                    print("   No categories yet.")

            elif command == 'stats':
                stats = memory_store.get_stats()
                print(f"\n📊 Storage Statistics:")
                print(f"   Total memories: {stats['total_memories']}")
                print(f"   Categories: {', '.join(stats['categories'].keys()) if stats['categories'] else 'None'}")
                print(f"   Storage path: {stats['storage_path']}")

            elif command == 'clear':
                if ':' in parts[1]:
                    category = parts[1].split(':')[1]
                    deleted = memory_store.delete_memory(category=category)
                else:
                    key = parts[1]
                    deleted = memory_store.delete_memory(key=key)

            else:
                print("   Unknown command. Try: save, get, list, stats, clear, quit")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        demo_memory_system()
    else:
        print("🧠 Claude Code with Local Memory System")
        print("\nUsage:")
        print("  python3 claude_code.py --demo    # Interactive memory demo")
        print("  python3 claude_code.py           # API mode (import in your code)")
        print("\nImport in your project:")
        print("  from claude_code import claude_with_memory, LocalMemoryStore")

# ============================================================================
# 使用示例（在您的项目中导入使用）：
# ============================================================================

"""
示例 1: 基本记忆存储和检索
```python
from claude_code import LocalMemoryStore

# 创建记忆存储实例
memory = LocalMemoryStore()

# 保存一条记忆
memory.save_memory(
    key="project_info",
    content="这是一个 OPM 综合业务系统，使用 Python 开发。",
    category="project"
)

# 检索记忆
memories = memory.get_memories(key="project_info")
for mem in memories:
    print(mem['content'])

# 按分类检索所有记忆
all_project_memories = memory.get_memories(category="project")
```

示例 2: 与 Claude API 集成使用
```python
from claude_code import claude_with_memory

# 带记忆的 Claude 对话
response = claude_with_memory(
    prompt="帮我设计一个用户管理系统",
    memory_key="project_requirements",
    category="development"
)

# 后续对话会自动加载之前的记忆
response2 = claude_with_memory(
    prompt="现在需要添加权限管理模块",
    memory_key="project_requirements",
    category="development"
)
```

示例 3: 交互式记忆管理
```bash
# 启动交互式记忆系统
./start_with_claude.sh memory

# 可用命令：
# save <key> <content>    - 保存记忆
# get <key>               - 检索特定记忆
# get category:<category> - 按分类检索
# list                    - 列出所有分类
# stats                   - 查看存储统计
# clear <key>             - 删除记忆
# quit                    - 退出
```

示例 4: 获取记忆上下文用于提示词增强
```python
from claude_code import LocalMemoryStore

memory = LocalMemoryStore()

# 获取格式化的记忆上下文
context = memory.get_memory_context(
    key="user_preferences",
    category="user_profile",
    max_memories=3  # 最多返回 3 条记忆
)

# context 可以直接拼接到你的 prompt 中
full_prompt = f"{context}\n{user_input}"
```

示例 5: 查看记忆存储统计
```python
from claude_code import LocalMemoryStore

memory = LocalMemoryStore()
stats = memory.get_stats()

print(f"总记忆数: {stats['total_memories']}")
print(f"分类: {stats['categories']}")
print(f"存储路径: {stats['storage_path']}")
```
"""