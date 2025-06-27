mkdir leads
set sourceDir=E:\MyDocs\Programming\GisNyc\hldata\V2data
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
REM xcopy "%sourceDir%\places_standbyused\" ".\leads" %options%
xcopy "%sourceDir%\places_userwhite\" ".\leads" %options%
xcopy "%sourceDir%\places_useryellow\" ".\leads" %options%
xcopy "%sourceDir%\places_yellow\" ".\leads" %options%
xcopy "%sourceDir%\places_specialops\" ".\leads" %options%
xcopy "%sourceDir%\places_extras\" ".\leads" %options%

mkdir other
xcopy "%sourceDir%\locs\" ".\other" %options%
xcopy "%sourceDir%\blocks\" ".\other" %options%
xcopy "%sourceDir%\regions\" ".\other" %options%

mkdir leadsCombined
xcopy "%sourceDir%\people_formap\" ".\leadsCombined" %options%
xcopy "%sourceDir%\places_formap\" ".\leadsCombined" %options%