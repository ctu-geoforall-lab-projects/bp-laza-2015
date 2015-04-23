SVGFILES = $(shell ls *.svg)
SVGPNGFILES = $(patsubst %.svg, %.png, $(SVGFILES))
PNGFILES = $(SVGPNGFILES)

all: $(PNGFILES)

$(SVGPNGFILES): %.png: %.svg
	convert -geometry 1440 $< $@

clean:
	rm -rf $(PNGFILES) $(SVGPNGFILES)
