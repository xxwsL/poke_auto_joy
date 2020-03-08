#!/bin/bash
pid=$(ps -aux | grep 'python3 start.py -date' | awk '{print $2}' | head -n 1)
kill -9 $pid