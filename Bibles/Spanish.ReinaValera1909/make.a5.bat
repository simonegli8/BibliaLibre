chcp 65001
bibmark

cd tex
xelatex Biblia10ptA5 -output-directory=..\out\pdf
xelatex Biblia10ptA5 -output-directory=..\out\pdf

cd ..\out\pdf
move Biblia10ptA5.pdf ReinaValera1909.10pt.A5.pdf

cd ..\..\