# -*- coding: utf-8 -*-
from django.conf import settings

PHOTO_UPLOAD_TO = getattr(settings, 'PHOTO_UPLOAD_TO', 'photos')
PHOTO_PAGINATE_BY = 30