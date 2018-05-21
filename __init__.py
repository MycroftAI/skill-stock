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
import xml.etree.ElementTree as ET

import requests
from adapt.intent import IntentBuilder
from os.path import dirname

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'eward'
logger = getLogger(__name__)


class StockSkill(MycroftSkill):
    def __init__(self):
        super(StockSkill, self).__init__(name="StockSkill")

    def initialize(self):
        stock_price_intent = IntentBuilder("StockPriceIntent") \
            .require("StockPriceKeyword").require("Company").build()
        self.register_intent(stock_price_intent,
                             self.handle_stock_price_intent)

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

        except:
            self.speak_dialog("not.found", data={'company': company})

    def _query(self, url, param_name, query):
        payload = {param_name: query}
        response = requests.get(url, params=payload)
        return ET.fromstring(response.content)

    def find_and_query(self, query):
        root = self._query(
            "http://dev.markitondemand.com/MODApis/Api/v2/Lookup?",
            'input', query)
        root = self._query(
            "http://dev.markitondemand.com/Api/v2/Quote?", 'symbol',
            root.iter('Symbol').next().text)
        return {'symbol': root.iter('Symbol').next().text,
                'company': root.iter('Name').next().text,
                'price': root.iter('LastPrice').next().text}

    def stop(self):
        pass


def create_skill():
    return StockSkill()
