# custom validators

import os
from django.core.exceptions import ValidationError


def validateGameFile(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    validExtensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if not ext.lower() in validExtensions:
        raise ValidationError('Unsupported file extension; must be from: [{}]'.format(','.join(validExtensions)))

