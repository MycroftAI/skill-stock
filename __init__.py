# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import requests

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.util.parse import match_one


COMPANY_ALIASES = {
    'google': 'Alphabet inc'
}

# These are the endpoints for the financial modeling prep open API
API_URL = 'https://financialmodelingprep.com/api/v3/'
SEARCH_QUERY = API_URL + 'search?query={}&limit=10'
PROFILE_QUERY = API_URL + 'company/profile/{}'


def search_company(query):
    """Search for a company and return the ticker symbol."""
    lookup = requests.get(SEARCH_QUERY.format(query))
    if 200 <= lookup.status_code < 300:
        if len(lookup.json()) == 0:
            return None # Nothing found
        else:
            # Create dict with company name as key
            company_dict = {c['name'].lower(): c for c in lookup.json()}
            info, confidence = match_one(query.lower(), company_dict)
            # Return None if the confidence is too low otherwise
            # return the closest match.
            return info['symbol'] if confidence > 0.5 else None
    else:
        # HTTP Status indicates something went wrong
        raise requests.HTTPError('API returned status code: '
                                 '{}'.format(response.status_code))


def get_company_profile(symbol):
    """Get the profile of a company given the symbol."""
    response = requests.get(PROFILE_QUERY.format(symbol))
    if 200 <= response.status_code < 300:
        return response.json().get('profile', {})
    else:
        raise requests.HTTPError('API returned status code: '
                                 '{}'.format(response.status_code))


def find_and_query(query):
    """Find company symbol and query for information."""
    symbol = search_company(query)
    if symbol:
        profile = get_company_profile(symbol)
        return {'symbol': symbol,
                'company': profile['companyName'],
                'price': str(profile['price'])}
    else:
        return None


class StockSkill(MycroftSkill):
    @intent_handler(IntentBuilder("")
                    .require("StockPriceKeyword").require("Company"))
    def handle_stock_price_intent(self, message):
        company = message.data.get("Company")
        if company in COMPANY_ALIASES:
            query_company = COMPANY_ALIASES[company]
        else:
            query_company = company

        try:
            response = find_and_query(query_company)
            self.bus.once("recognizer_loop:audio_output_start",
                          self.enclosure.mouth_text(
                              response['symbol'] + ": " + response['price']))
            self.enclosure.deactivate_mouth_events()
            self.speak_dialog("stock.price", data=response)
            time.sleep(12)
            self.enclosure.activate_mouth_events()
            self.enclosure.mouth_reset()

        except requests.HTTPError as e:
            self.speak_dialog("api.error", data={'error': str(e)})
        except Exception as e:
            self.log.exception(e)
            self.speak_dialog("not.found", data={'company': company})


def create_skill():
    return StockSkill()
