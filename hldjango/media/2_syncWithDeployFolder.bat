REM This folder should be sync'd with deploy folder before deploying...

xcopy "downloads" "../deploy/media/downloads" /E /I /H /Y
xcopy "shared" "../deploy/media/shared" /E /I /H /Y
xcopy "hldata" "../deploy/media/hldata" /E /I /H /Y