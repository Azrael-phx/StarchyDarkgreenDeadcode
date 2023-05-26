#from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views import View
from google_auth_oauthlib.flow import Flow
from django.conf import settings
#from django.urls import reverse
from requests_oauthlib import OAuth2Session
import json
import secrets
from django.views.generic import TemplateView


#constants for auth configuration
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']
REDIRECT_URI = 'https://starchydarkgreendeadcode.ray20.repl.co/rest/v1/calendar/redirect/'
state = secrets.token_urlsafe(16)


class MyHomePageView(TemplateView):
    template_name = 'templates/index.html'

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            settings.CLIENT_SECRET_FILE,
            scopes=settings.SCOPES,
            redirect_uri=REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Save the state in the session for later verification in the callback view
        request.session['oauth_state'] = state

        return redirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Get the authorization code from the query parameters
        code = request.GET.get('code')

        # Check if the state is valid
        if 'oauth2_state' not in request.session or 'oauth2_state' not in request.GET or \
                request.GET['state'] != request.session['oauth2_state']:
            # Invalid state, handle accordingly
            return HttpResponse('Invalid OAuth2 state')

        # Configuration
        client_id = "422948648577-h0hueb6eu5uiho2afd8ma831huuh8t02.apps.googleusercontent.com"
        client_secret = "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"
        redirect_uri = REDIRECT_URI
        token_url = 'https://accounts.google.com/o/oauth2/token'

        # Initialize OAuth2 session
        oauth2_session = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )

        # Exchange authorization code for access token
        token = oauth2_session.fetch_token(
            token_url=token_url,
            authorization_response=request.build_absolute_uri(),
            code=code,
        )

        # Get the access token
        access_token = token.get('access_token')

        # Use the access token to make API requests
        event_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Send request to retrieve events
        response = oauth2_session.get(event_url, headers=headers)

        if response.status_code == 200:
            # Events retrieved successfully
            events = response.json()
            # Process and handle the events data as needed
            return HttpResponse(json.dumps(events), content_type='application/json')
        else:
            # Error occurred while retrieving events
            return HttpResponse('Error retrieving events')

