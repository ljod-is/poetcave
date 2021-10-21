{% load i18n %}
{% load mailurl %}

{% blocktrans %}We appreciate you using our website for storing and sharing your poems. Unfortunately, not all poems can be accepted for public display on our website. That doesn't mean that such poems are bad, it just means that it doesn't fulfill the conditions that we have had to set for publicly displaying it on our website.{% endblocktrans %}

{% blocktrans with poem_name=poem.name %}Unfortunately, one of your poems, named "{{ poem_name }}" has been **rejected** by one of our moderators.{% endblocktrans %}

{% blocktrans %}You can get more information on the matter by viewing your poem on our website, while logged in:{% endblocktrans %} [{{ pome.name }}]({% mailurl 'poem' poem.id %})
