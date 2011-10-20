# -*- coding: utf-8 -*-
"""
    HTML form definitions for Marcel

    :copyright: (c) 2011 By Ori Livneh
    :license: GPLv3, see LICENSE for more details.
"""
from flaskext.wtf import (
    Form,
    SelectField,
    TextAreaField,
    TextField,
    validators
)


class EntryForm(Form):
    """ Represents an HTML form for a Marcel entry """
    entry_type = SelectField(
        label='Type of Entry',
        choices=[('request', 'I have a request'),
                 ('offer', 'I have something to offer')]
    )

    summary = TextField(
        label='Summary',
        validators=[validators.Length(max=140), validators.Required()],
        description="Headline for your entry, in 140 characters or fewer"
    )

    details = TextAreaField(
        label='Details',
        validators=[validators.Length(max=1000), validators.Required()],
        description="1000 characters max."
    )

    contact_info = TextField(
        label='Contact Information',
        validators=[validators.Length(max=140), validators.Required()],
        description="A phone number, email address, location, etc."
    )
