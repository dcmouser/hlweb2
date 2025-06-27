REM HERE IS HOW TO USE THIS:
REM THIS IS JUST USED TO *COMPILE* .po files to .mo where they can be used, so run this after running stage 1

python C:\Users\jesse\anaconda3\Tools\i18n\msgfmt.py -o code/lib/casebook/locale/en/LC_MESSAGES/casebook.mo code/lib/casebook/locale/en/LC_MESSAGES/casebook.po
python C:\Users\jesse\anaconda3\Tools\i18n\msgfmt.py -o code/lib/casebook/locale/es/LC_MESSAGES/casebook.mo code/lib/casebook/locale/es/LC_MESSAGES/casebook.po
python C:\Users\jesse\anaconda3\Tools\i18n\msgfmt.py -o code/lib/casebook/locale/sv/LC_MESSAGES/casebook.mo code/lib/casebook/locale/sv/LC_MESSAGES/casebook.po