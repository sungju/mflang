#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Usage> $0 <mf filename> <character name>"
	echo 
	echo "      ex) $0 beta B"
	exit 1
fi

filename=$1
char=$2
mf ${filename}.mf
# Create a proof-mode file and show it up
gftodvi ${filename}.2602gf
xdvi ${filename}.dvi

# Create a font file for TeX use
mf "\mode=ljfour; mode_setup; input ${filename}.mf"
gftopk ${filename}.600gf ${filename}.pk

cat <<EOF > test_${filename}.tex
\documentclass{article}

\newfont{\letter${filename}}{${filename}}
\newcommand{\other${filename}}{{\letter${filename} ${char}}}

\begin{document}

Let's try having a strange \other${filename}\ here.

\end{document}
EOF

latex test_${filename}.tex
xdvi test_${filename}.dvi
