set sourceDir=E:\MyDocs\Programming\GisNyc\hldata\Directory\Manhattan\latex\pdf
set destDir=.\downloads\newYorkNoir_materials_v3
set options=/E /y
xcopy "%sourceDir%\directoryWhite.pdf" ".\%destdir%\directoriesAndMaps\" %options%
xcopy "%sourceDir%\directoryYellow.pdf" ".\%destdir%\directoriesAndMaps\" %options%
xcopy "%sourceDir%\directoryReverse.pdf" ".\%destdir%\directoriesAndMaps\" %options%
xcopy "%sourceDir%\MapAtlas85x11Interleaved.pdf" ".\%destdir%\directoriesAndMaps\" %options%
xcopy "%sourceDir%\directoryFingerprints.pdf" ".\%destdir%\directoriesAndMaps\" %options%
xcopy "%sourceDir%\directoryCriminalHistory.pdf" ".\%destdir%\directoriesAndMaps\" %options%

xcopy "%sourceDir%\StreetGuide.pdf" ".\%destdir%\rulesAndGuides\" %options%

xcopy "E:\MyDocs\Programming\Python\NynInterleaveMap\mapAtlas\MapAtlas85x11Interleaved.pdf" ".\%destdir%\directoriesAndMaps\" %options%

set destDir=.\downloads\newYorkNoir_authorMaterials_v3
xcopy "%sourceDir%\*.pdf" ".\%destdir%" %options%
del "%destdir%\directoryWhite.pdf"
del "%destdir%\directoryYellow.pdf"
del "%destdir%\directoryReverse.pdf"
del "%destdir%\MapAtlas85x11Interleaved.pdf"
del "%destdir%\directoryFingerprints.pdf"
del "%destdir%\directoryCriminalHistory.pdf"

del ".\downloads\newYorkNoir_authorMaterials_v3.zip"
del ".\downloads\newYorkNoir_materials_v3.zip"
del ".\downloads\newYorkNoir_rulesEtc.zip"

"C:\Program Files\7-Zip\7z.exe" a ".\downloads\newYorkNoir_authorMaterials_v3.zip" ".\downloads\newYorkNoir_authorMaterials_v3"
"C:\Program Files\7-Zip\7z.exe" a ".\downloads\newYorkNoir_Materials_v3.zip" ".\downloads\newYorkNoir_Materials_v3"
"C:\Program Files\7-Zip\7z.exe" a ".\downloads\newYorkNoir_rulesEtc.zip" ".\downloads\newYorkNoir_Materials_v3\rulesAndGuides" ".\downloads\newYorkNoir_Materials_v3\extras" ".\downloads\newYorkNoir_Materials_v3\sheets"