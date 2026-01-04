#!/bin/bash
cd Bibles/English.WorldEnglishBibleGB

chmod +x make.sh
./make.sh

cd ../../Bibles/English.WorldEnglishBibleUS

chmod +x make.sh
./make.sh

cd ../../Bibles/German.Schlachter1951

chmod +x make.sh
./make.sh

cd ../../Bibles/Spanish.ReinaValera1909

chmod +x make.sh
./make.sh

cd ../..