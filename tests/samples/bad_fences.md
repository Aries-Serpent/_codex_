# test_validate_fences.md
## Valid (backticks)
```python
print("ok")
```

## Valid (tildes)
~~~md
# heading
~~~

## Invalid: closing shorter than opening
````text
outer
```
````

## Invalid: backticks in info string (backtick fence)
```py`thon
print("nope")
```

## House-rule violation: inner closing-line equals opener
````markdown
```bash
echo hi
```
````
