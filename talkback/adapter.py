#!/usr/bin/env python

import subprocess

class Adapter:
    def ask(self, question):
        output = subprocess.Popen(["howdoi", question], stdout=subprocess.PIPE)
        return output.stdout.read()
