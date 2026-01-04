chcp 65001
..\..\bin\bibmark.exe

cd tex
xelatex -jobname=WorldEnglishBibleGB11ptB5 -output-directory ..\out\pdf Bible11ptB5.tex
cd ..
