SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

help:
@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

.PHONY: help Makefile

%: Makefile
@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)"

html:
@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
@echo "Build finished. HTML pages are in $(BUILDDIR)/html"

clean:
rm -rf $(BUILDDIR)
