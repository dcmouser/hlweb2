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
xcopy "%sourceDir%\places_standbyused\" ".\leads" %options%
xcopy "%sourceDir%\places_userwhite\" ".\leads" %options%
xcopy "%sourceDir%\places_useryellow\" ".\leads" %options%
xcopy "%sourceDir%\places_yellow\" ".\leads" %options%
