# Universal RAG Chunker

This original example can be used to explore source-traceable chunking.
这一示例不依赖特定行业，保留原始文字与来源位置。

## Installation example

```python
# This line belongs to code, not the document heading hierarchy.
print("Hello, 世界")
```

## Practical notes

- A source span points to text in a Document IR block.
- Character counts are Unicode code points, not model tokens.
- Formula and image references remain in the source text: x = 2, ![](diagram.png).
