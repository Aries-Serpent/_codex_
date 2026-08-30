# test_validate_fences.md
## Valid (backticks)
```python
print("ok")
```text

## Valid (tildes)
~~~md
# heading
~~~

## Invalid: closing shorter than opening
````text
outer
````text
````

## Invalid: backticks in info string (backtick fence)
````py`thon
print("nope")
```text

## House-rule violation: inner closing-line equals opener
````markdown
````bash
echo hi
```text
````

```
