mkdir leads
set sourceDir=E:\MyDocs\Programming\GisNyc\hldata\PhaseTwoB
set destDir=.
set options=/E /y
xcopy "%sourceDir%\unusedLeads\unusedLeads.csv" "." %options%

REM xcopy "%sourceDir%\people_manual\" ".\leads" %options%
REM xcopy "%sourceDir%\places_bestny\" ".\leads" %options%
REM xcopy "%sourceDir%\places_extras\" ".\leads" %options%
REM xcopy "%sourceDir%\places_grid\" ".\leads" %options%
REM xcopy "%sourceDir%\places_manual\" ".\leads" %options%
REM xcopy "%sourceDir%\places_outer\" ".\leads" %options%
REM xcopy "%sourceDir%\places_people\" ".\leads" %options%
REM xcopy "%sourceDir%\places_poijr\" ".\leads" %options%
REM xcopy "%sourceDir%\places_userwhite\" ".\leads" %options%
REM xcopy "%sourceDir%\places_useryellow\" ".\leads" %options%
REM xcopy "%sourceDir%\places_yellow\" ".\leads" %options%
REM xcopy "%sourceDir%\places_specialops\" ".\leads" %options%
REM xcopy "%sourceDir%\places_extras\" ".\leads" %options%

mkdir other
xcopy "%sourceDir%\locs\" ".\other" %options%
xcopy "%sourceDir%\blocks\" ".\other" %options%
xcopy "%sourceDir%\regions\" ".\other" %options%

mkdir leadsCombined
xcopy "%sourceDir%\people_formap\" ".\leadsCombined" %options%
xcopy "%sourceDir%\places_formap\" ".\leadsCombined" %options%
xcopy "%sourceDir%\places_formap_allinone\" ".\leadsCombined" %options%

mkdir criminalHistory
xcopy "%sourceDir%\places_criminal_history\" ".\criminalHistory" %options%
xcopy "%sourceDir%\places_criminal_history_manual\" ".\criminalHistory" %options%


del ".\leadsCombined\people_formap.json.gz"
del ".\leadsCombined\places_formap.json.gz"
del ".\leadsCombined\places_formap_allinone.json.gz"

"C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\people_formap.json.gz" ".\leadsCombined\people_formap.json"
"C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\places_formap.json.gz" ".\leadsCombined\places_formap.json"
"C:\Program Files\7-Zip\7z.exe" a -tgzip ".\leadsCombined\places_formap_allinone.json.gz" ".\leadsCombined\places_formap_allinone.json"