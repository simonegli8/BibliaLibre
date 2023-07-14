chcp 65001
..\..\bin\bibmark.exe -replace /HErrn/[Herrn]{.smallcaps}/HErr/[Herr]{.smallcaps}

cd out\pandoc\epub
pandoc -o ..\..\epub\BibelFreieLuther.epub --epub-embed-font "..\..\..\..\..\Fonts\DayRoman*.ttf" --css=..\..\..\style.css 00.0-Inhaltsverzeichnis.md 00.1-Impressum.md 00.2-Vorwort.md "01-1. Mose.md" "02-2. Mose.md" "03-3. Mose.md" "04-4. Mose.md" "05-5. Mose.md" 06-Josua.md 07-Richter.md 08-Ruth.md "09-1. Samuel.md" "10-2. Samuel.md" "11-1. Könige.md" "12-2. Könige.md" "13-1. Chronik.md" "14-2. Chronik.md" 15-Esra.md 16-Nehemia.md 17-Esther.md 18-Hiob.md 19-Psalm.md 20-Sprüche.md 21-Prediger.md "22-Hoheslied.md" 23-Jesaja.md 24-Jeremia.md 25-Klagelieder.md 26-Hesekiel.md 27-Daniel.md 28-Hosea.md 29-Joel.md 30-Amos.md 31-Obadja.md 32-Jona.md 33-Micha.md 34-Nahum.md 35-Habakuk.md 36-Zephanja.md 37-Haggai.md 38-Sacharja.md 39-Maleachi.md "40-Matthäus.md" "41-Markus.md" "42-Lukas.md" "43-Johannes.md" 44-Apostelgeschichte.md 45-Römer.md "46-1. Korinther.md" "47-2. Korinther.md" 48-Galater.md 49-Epheser.md 50-Philipper.md 51-Kolosser.md "52-1. Thessalonicher.md" "53-2. Thessalonicher.md" "54-1. Timotheus.md" "55-2. Timotheus.md" 56-Titus.md 57-Philemon.md 58-Hebräer.md 59-Jakobus.md "60-1. Petrus.md" "61-2. Petrus.md" "62-1. Johannes.md" "63-2. Johannes.md" "64-3. Johannes.md" "65-Judas.md" "66-Offenbarung.md" 

cd ..\..\..