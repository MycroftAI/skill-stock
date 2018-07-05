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


class StockSkill(MycroftSkill):
    @intent_handler(IntentBuilder("") \
            .require("StockPriceKeyword").require("Company"))
    def handle_stock_price_intent(self, message):
        company = message.data.get("Company")
        try:
            response = self.find_and_query(company)
            self.emitter.once("recognizer_loop:audio_output_start",
                              self.enclosure.mouth_text(
                                  response['symbol'] + ": " + response[
                                      'price']))
            self.enclosure.deactivate_mouth_events()
            self.speak_dialog("stock.price", data=response)
            time.sleep(12)
            self.enclosure.activate_mouth_events()
            self.enclosure.mouth_reset()

        except Exception as e:
            self.log.exception(e)
            self.speak_dialog("not.found", data={'company': company})

    def _query(self, url, param_name, query):
        payload = {param_name: query}
        response = requests.get(url, params=payload)
        return response

    def find_and_query(self, query):
        lookup = self._query(
            "http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?",
            'input', query)
        symbol = lookup.json()[0]['Symbol'] if len(lookup.json()) > 0 else None
        if symbol:
            quote = self._query(
                "http://dev.markitondemand.com/Api/v2/Quote/json?",
                'symbol', symbol)
            return {'symbol': symbol,
                    'company': lookup.json()[0].get('Name'),
                    'price': str(quote.json()['LastPrice'])}
        return None

    def stop(self):
        pass


def create_skill():
    return StockSkill()
