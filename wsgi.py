#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 11:28:24 2020

@author: bramante
"""

#............................Binding for Gunicorn..............................
from run import application

if __name__ == "__main__":
    application.run()