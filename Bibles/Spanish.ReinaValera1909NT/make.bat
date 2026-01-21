chcp 65001
bibmark

cd tex
xelatex Biblia11ptA5 -output-directory=..\out\pdf
xelatex Biblia11ptA5 -output-directory=..\out\pdf

cd ..\out\pdf
move Biblia11ptA5.pdf ReinaValera1909NT.11pt.A5.pdf

cd ..\..\