{% load i18n %}
{% load mailurl %}

{% blocktrans with poem_name=poem.name %}Happily, one of your poems, named "{{ poem_name }}" has been **approved** by one of our moderators.{% endblocktrans %}

{% blocktrans %}Everyone can now read it, in all its glory, at our website:{% endblocktrans %} [{{ poem.name }}]({% mailurl 'poem' poem.id %})
