mkdir leads
set sourceDir=E:\MyDocs\Programming\GisNyc\hldata\PhaseTwoB
set destDir=.
set options=/E /y
xcopy "%sourceDir%\unusedLeads\unusedLeads.csv" "." %options%

xcopy "%sourceDir%\people_manual\" ".\leads" %options%
xcopy "%sourceDir%\places_bestny\" ".\leads" %options%
xcopy "%sourceDir%\places_extras\" ".\leads" %options%
xcopy "%sourceDir%\places_grid\" ".\leads" %options%
xcopy "%sourceDir%\places_manual\" ".\leads" %options%
xcopy "%sourceDir%\places_outer\" ".\leads" %options%
xcopy "%sourceDir%\places_people\" ".\leads" %options%
xcopy "%sourceDir%\places_poijr\" ".\leads" %options%
xcopy "%sourceDir%\places_userwhite\" ".\leads" %options%
xcopy "%sourceDir%\places_useryellow\" ".\leads" %options%
xcopy "%sourceDir%\places_yellow\" ".\leads" %options%
xcopy "%sourceDir%\places_specialops\" ".\leads" %options%
xcopy "%sourceDir%\places_extras\" ".\leads" %options%

xcopy "%sourceDir%\fingerprintData\fingerprintData.json" ".\fingerprintData" %options%

mkdir other
xcopy "%sourceDir%\locs\" ".\other" %options%
xcopy "%sourceDir%\blocks\" ".\other" %options%
xcopy "%sourceDir%\regions\" ".\other" %options%

mkdir leadsCombined
REM xcopy "%sourceDir%\people_formap\" ".\leadsCombined" %options%
REM xcopy "%sourceDir%\places_formap\" ".\leadsCombined" %options%
REM xcopy "%sourceDir%\places_formap_allinone\" ".\leadsCombined" %options%

REM del ".\leadsCombined\people_formap.json.gz"
REM del ".\leadsCombined\places_formap.json.gz"
REM del ".\leadsCombined\places_formap_allinone.json.gz"

REM "C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\people_formap.json.gz" ".\leadsCombined\people_formap.json"
REM "C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\places_formap.json.gz" ".\leadsCombined\places_formap.json"
REM "C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\places_formap_allinone.json.gz" ".\leadsCombined\places_formap_allinone.json"