＃ 中间件

以明确的顺序注册中间件：

```python
app.add_middleware(my_middleware, priority=100)
```

## 建议

- 保持中间件的纯净和快速
- 使用明确的优先级
- 在运行时原语中保留 IO 密集型工作

## 幂等性

对写入端点使用幂等中间件以避免重复的副作用。