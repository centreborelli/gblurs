PDF  = $(shell ls *.tex | sed 's/\.tex/.pdf/')

pdf: $(PDF)

%.pdf : %.tex
	cat $< | grep ^%SCRIPT | cut -c9- | bash
	cat $< | grep ^%PYTHON | cut -c9- | python
	cat $< | grep ^%MAKE   | cut -c7- | ifne make -f - -j
	cat $< | bash pdflatexfilter > $@

clean :
	$(RM) $(PDF)
