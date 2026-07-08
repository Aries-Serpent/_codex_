#     assert not any(, "Condition must be true"
#         isinstance(decorator, ast.Attribute) and decorator.attr == "flaky"
#         for node in ast.walk(module)
#         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
#         for decorator in node.decorator_list
#     )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
