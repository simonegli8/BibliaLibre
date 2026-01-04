chcp 65001
bibmark -twolanguage ..\Spanish.ReinaValera1909 ..\English.WorldEnglishBibleUS

cd tex
xelatex -file-line-error Biblia9ptB5
del BibliaParaAprenderIngles9ptB5.pdf
ren Biblia9ptB5.pdf BibliaParaAprenderIngles9ptB5.pdf

del ..\out\BibliaParaAprenderIngles9ptB5.pdf
move BibliaParaAprenderIngles9ptB5.pdf ..\out

cd ..
