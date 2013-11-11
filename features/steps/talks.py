from behave import *

@given(u'PythonFOSDEM is setup')
def step_impl(context):
    assert context.client

@when(u'I connect with {email} and "{password}"')
def step_impl(context, email, password):
    values = dict(
        email=email,
        password=password,
    )

    response = context.client.post(context.login_user_url,
                                   data=values,
                                   follow_redirects=True)
    assert response.status_code == 200

@when(u'I create a talk "{title}" at {site_url}')
def step_impl(context, title, site_url):
    values = dict(
        title=title,
        description='Description',
        twitter='@twitter',
        site_url=site_url,
        level='beginner'
    )

    response = context.client.post(context.talk_submit_url,
                                   data=values,
                                   follow_redirects=True)
    assert response.status_code == 200
