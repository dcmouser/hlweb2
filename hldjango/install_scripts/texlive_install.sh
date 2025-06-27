#!/usr/bin/env sh

# ATTN: JR - occasionally this build fails because it picks a random CTAN MIRROR that is "untrusted" which aborts install

# based on https://github.com/latex3/latex3/blob/main/support/texlive.sh


# ATTN: JR ADDED - i think this MUST happen in Dockerfile now -- i dont THINK it sticks if we set this here
# ATTN: *IMPORTANT* The directory we add to path is in the install directory specified in the file .\textlive.profile
export PATH=/opt/texlive/bin/x86_64-linux:$PATH


# ATTN: JR - disabling this if check for cached TL
# See if there is a cached version of TL available
# if ! command -v texlua > /dev/null; then
  # Obtain TeX Live

  # use official set of mirrors -- this sometimes fails due to a bad mirror with bad sinature
  #wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
  # manually specify source
  wget http://ctan.math.illinois.edu/systems/texlive/tlnet/install-tl-unx.tar.gz

  tar -xzf install-tl-unx.tar.gz
  cd install-tl-20*

  # Install a minimal system (we are inside install-tl-20* directory so need to refer to profile file in parent dir)
  ./install-tl --profile=../texlive.profile

  cd ..
# fi

# Update tlmgr itself
tlmgr update --self




# ATTN: JR - texlive package sets
# see https://tex.stackexchange.com/questions/245982/differences-between-texlive-packages-in-linux

# extra? no we just specify the packages we want
#tlmgr install texlive-latex-extra 

# pictures? no we don't need all these, we will manually specify the image support packages we want
#tlmgr install collection-pictures

# ATTN: JR - baseline set of fonts (not needed but maybe in future)
tlmgr install collection-fontsrecommended

# ATTN: JR - Big set of fonts (not needed but maybe in future)
#tlmgr install collection-fontsextra


# ATTN: JR - Other packages to consider:
# handwriting fonts see https://www.tug.org/FontCatalogue/calligraphicalfonts.html



# For the doc target and testing l3doc
# PACKAGE INSTALL LIST UPDATED 10/25/24 - NOTE THIS REQUIRED LOTS OF TRIAL AND ERROR BUILDING LOCAL HLWEB_PERSONAL and testing a build of wrongbook_partial, and then checking log for latex build errors about missing sty files that required manually adding package
# for some reason accessory packages with sty files are not being found during this tlmgr install, so i have to search web for what packages have them, etc.
tlmgr install \
  xelatex \
  xetex \
	hyperref \
	ulem \
	graphicx \
	amsmath \
	amsfonts \
	amssymb \
	csquotes \
	listings \
	fontenc \
	inputenc \
	lmodern \
	textcomp \
	lastpage \
	FiraSans \
	librebaskerville \
	baskervillef \
	setspace \
	MnSymbol \
	parskip \
	scrlayer-scrpage \
	tocloft \
	multicol \
	tikz \
	tikzfill \
	clock \
	ifsym \
	fontawesome5 \
	pngfornament \
	fancybox \
	pdfpages \
	aurical \
	babel \
	koma-script \
	fira \
	xkeyval \
	xkvutils \
	fontaxes \
	mnsymbol \
	pgf \
	pgfornament \
	pgfopts \
	pdflscape \
	csquotes \
	fancybox \
	aurical \
	listings \
	listingsutf8 \
	pdfpages \
	enumitem \
	refcount \
	tabularray \
	adjustbox \
	printlen \
	tcolorbox \
	options \
	pict2e \
	pdfcol \
	mdwtools \
	ellipse \
	longfbox \
	lettrine \
	lipsum \
	marginnote \
  picinpar \
  yfonts \
	float \
	caption \
	needspace \
	eso-pic \
	lscape \
	etoolbox \
	fontspec \
	ninecolors \
	xcolor \
	censor \
	pbox \
	tokcycle \
	ulem \
	soul \
	wrapfig \
	tabularx



# Keep no backups (not required, simply makes cache bigger)
tlmgr option -- autobackup 0

# Update the TL install but add nothing new
tlmgr update --all --no-auto-install

