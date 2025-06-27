REM THESE ARE FROM run_mainservices.sh
REM YOU SHOULD "POETRY SHELL" first before you run these

python ./manage.py makemigrations
python ./manage.py migrate

python ./manage.py initGameGroupAndPermission
python ./manage.py initSiteGadminGroupAndPermission
python ./manage.py verifyOrAddInsecureTestingSuperuser

python ./manage.py collectstatic