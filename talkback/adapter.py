#!/usr/bin/env python

import subprocess

class Adapter:

    __howdoi_trigger = "howdoi"

    def ask(self, question):
        output = subprocess.Popen([self.__howdoi_trigger, self.question_parser(question)], stdout=subprocess.PIPE)
        return output.stdout.read()

    def question_parser(self, question):
        return question.replace(self.__howdoi_trigger, "")
