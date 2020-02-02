#!/usr/bin/python3

import sys
import ts3musicbot

if __name__ == '__main__':
	args = ""
	
	for a in sys.argv[1:]:
		args = args + a
	
	if len(args) > 0:
		ts3musicbot.run(args=args)
	else:
		ts3musicbot.run()