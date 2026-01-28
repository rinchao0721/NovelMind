"""
Test Neo4j connection from backend
"""

import asyncio
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from database.neo4j_db import Neo4jDB
from config import settings


async def main():
    print("=" * 60)
    print("NovelMind Neo4j Connection Test")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  URI: {settings.NEO4J_URI}")
    print(f"  User: {settings.NEO4J_USER}")
    print(f"  Password: {'*' * len(settings.NEO4J_PASSWORD)}")
    print()

    neo4j = Neo4jDB()

    try:
        print("Testing connection...")
        result = await neo4j.test_connection()

        if result:
            print("✅ Connection successful!")
            print()

            # Test creating a sample character
            print("Testing character creation...")
            test_char = {
                "id": "test-001",
                "name": "测试人物",
                "novel_id": "test-novel",
                "importance": 0.8,
                "description": "这是一个测试人物",
            }

            char_id = await neo4j.create_character(test_char)
            print(f"✅ Created character node: {char_id}")
            print()

            # Test creating a relationship
            print("Testing relationship creation...")
            test_char2 = {
                "id": "test-002",
                "name": "测试人物2",
                "novel_id": "test-novel",
                "importance": 0.7,
                "description": "另一个测试人物",
            }
            await neo4j.create_character(test_char2)

            rel_result = await neo4j.create_relationship(
                "test-001",
                "test-002",
                "friend",
                {"strength": 0.9, "description": "好朋友关系", "first_chapter": 1},
            )
            print(f"✅ Created relationship: {rel_result}")
            print()

            # Clean up test data
            print("Cleaning up test data...")
            await neo4j.delete_novel_data("test-novel")
            print("✅ Cleanup complete")
            print()

            print("=" * 60)
            print("🎉 All tests passed! Neo4j is ready for use.")
            print("=" * 60)
        else:
            print("❌ Connection failed!")
            print()
            print("Troubleshooting:")
            print("1. Check if Neo4j container is running: docker ps | grep neo4j")
            print("2. Verify password in backend/.env matches container password")
            print("3. Check Neo4j logs: docker logs novelmind-neo4j")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Neo4j driver is not installed. Run: uv pip install neo4j")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await neo4j.close()


if __name__ == "__main__":
    asyncio.run(main())
