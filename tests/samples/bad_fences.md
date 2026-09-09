# test_validate_fences.md
## Invalid: closing shorter than opening
````text
outer
```
````

## Invalid: backticks in info string (backtick fence)
````py`thon
print("nope")
````
