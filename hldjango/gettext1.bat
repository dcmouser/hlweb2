REM HERE IS HOW TO USE THIS:
REM 1. RUN IT ONCE TO EXPORT ALL _("") string in all casebook source code files, and save into code/lib/casebook/locale/casebook.pot
REM 2. THEN MANUALLY COPY THAT .pot file to en/LC_MESSAGE and rename it from .pot to .po (OVERWRITING OLD)
REM 3. NOW, we have the base language file; but we need to compile it, so run the next batch files; here we compile only the english texts


python C:\Users\jesse\anaconda3\Tools\i18n\pygettext.py -d casebook -o code/lib/casebook/locale/casebook.pot code/lib/casebook/*.py

xcopy /Y code\lib\casebook\locale\casebook.pot code\lib\casebook\locale\en\LC_MESSAGES\casebook.po

python C:\Users\jesse\anaconda3\Tools\i18n\msgfmt.py -o code/lib/casebook/locale/en/LC_MESSAGES/casebook.mo code/lib/casebook/locale/en/LC_MESSAGES/casebook.po


python C:\Users\jesse\anaconda3\Tools\i18n\pygettext.py -o output.pot input.py
