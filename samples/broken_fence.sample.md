# Broken Fence Sample (should fail validator)

```diff
--- a/file.txt
+++ b/file.txt
@@
 some patch content
~~~  <-- mixed tilde fence (intentional error for testing)

End of file.

```