#!/usr/bin/python
from __future__ import print_function

import urllib2
import os
import json
import sys
import ssl
import socket
import calendar
import time
from subprocess import call

last_alert = 0.0

def get_json(url):
  loaded = False
  while not loaded:
    try:
      r = urllib2.urlopen(url).read()
      j = json.loads(r)
      loaded = True
    except ssl.SSLError:
      # another timeout
      print( "[!] SSL Error. Retrying...")
    except ValueError:
      # we didn't get a json back (probably an error page)
      print( "[!] ValueError. Retrying...")
    except socket.timeout:
      print( "[!] Socket timeout. Retrying...")
    except Exception as e:
      print( "[!] Error %s. Retrying..."%e)
  return j

def get_trades(exchange, since):
  """ Return the latest trades for a given exchange since a time in JSON format. """
  if exchange == "gox":
    url = "http://data.mtgox.com/api/1/BTCUSD/trades/fetch?since=%16d"%since
    #print "[*] URL: %s"%url
    trades = get_json(url)
    if trades["result"] == u'success':
      return trades
    else:
      print( "[!] Failure, retrying.")
      get_trades(exchange, since)
  else:
    print( "Exchange %s not found. Exiting."%exchange)
    sys.exit(1)

def calculate_vol( timeframe):
  """ Look back a timeframe (in seconds) and add up volume. """
  volume = 0.0
  since = time.time() - timeframe
  since  = float(since) * 1000000.0
  trades = get_trades("gox", since)
  #print "[*] Cutoff %16d"%since
  #print "[*] Num trades: %s"%len(trades["return"])
  for t in trades["return"]:
    tradetime = float(t["tid"])/1000000.0
    #if tradetime > since:
    #print "[*] Trade: %s > %d (end)"%(tradetime, end)
    volume += float(t["amount"])
    #else:
    #  return volume
  return volume

# ALERT WITH AUDIO
def find_player():
  """ Test a bunch of players, depending on platform to find one that works."""
  print( "[*] Searching for a player ...")
  if "linux" in sys.platform:
    # aplay
    try:
      call(["aplay", "--version"])
      return "aplay"
    except OSError:
      pass
    # oss
    try:
      if call(["ls","/dev/dsp"]) == 0:
        return "dsp"
    except:
      pass
    # vlc
    try:
      call(["vlc", "--version"])
      return "vlc"
    except OSError:
      pass
  else:
    print( "[!] Only supporting linux.")
  print( "[!] Fatal! no players found.")
  sys.exit(1)

def alert_audio( audiofile, player):
  if "linux" in sys.platform:
    if player == "aplay":
      call(["aplay", audiofile])
    elif player == "dsp":
      with open("/dev/null", "w") as f:
        call(["cat", audiofile], stdout=f)
    elif player == "vlc":
      call(["vlc", "-I dummy",audiofile])

# ALERT WITH EMAIL
def alert_email( host, sender, recipient,
                 subject='TRADING ALERT',
                 message='This is a trading alert',
                 port=587, encryption="tls"):
  """ Send an e-mail alert. Encryption options: tls, ssl, none."""
  import smtplib
  from email.mime.text import MIMEText
  msg = MIMEText("OMG CRASH!")
  msg['Subject'] = 'TRADING ALERT'
  msg['From'] = sender
  msg['To'] = recipient
  # tls
  if encryption == "tls":
    print( "[*] Connecting to e-mail server")
    s = smtplib.SMTP(host, port)
    print( "[*] Encrypting session.")
    s.starttls()
  # ssl
  elif encryption == "ssl":
    print( "[*] Connecting to e-mail server")
    s = smtplib.SMTP_SSL(host, port)
  # no encryption
  else:
    print( "[*] Connecting to e-mail server")
    s = smtplib.SMTP(host, port)
  s.sendmail(sender, [recipient], msg.as_string())
  s.quit()
  print( "[*] E-mail sent")

def get_args():
  import argparse
  desc = "Play an audio or send an e-mail alert when trade volume"\
         " in the past number of seconds reaches a specified amount."
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('exchange', type=str,
                      help='Which exchange to monitor: gox')
  parser.add_argument('timeframe', type=float,
                      help='Timeframe to look back in seconds')
  parser.add_argument('volume', type=float,
                      help='Volume threshold to alert above')
  parser.add_argument('alert_type', type=str,
                      help='Type of alert: audio, e-mail')
  parser.add_argument('--limit', type=float, default=300,
                      help='Wait this number of seconds between alerts. Default: 300')
  parser.add_argument('--audiofile', type=str, default="notify.wav",
                      help='Location of audio file to play. Default: notify.wav')
  parser.add_argument('--host', type=str, default="smtp.googlemail.com",
                      help='SMTP host')
  parser.add_argument('--port', type=int, default=587,
                      help='SMTP port')
  parser.add_argument('--sender', type=str, default="alert@my.host",
                      help='E-mail alert sender')
  parser.add_argument('--recipient', type=str, default="me@trad.er",
                      help='E-mail alert recipient')
  parser.add_argument('--subject', type=str, default="TRADE ALERT",
                      help='E-mail alert subject')
  parser.add_argument('--body', type=str, default="This is a trading alert.",
                      help='E-mail alert body')
  parser.add_argument('--encryption', type=str, default="tls",
                      help='SMTP server encryption: tls, ssl, none')
  return parser.parse_args()

if __name__ == "__main__":
  print( "###########################################################################")
  print( "#                          trade_alert by brand0                          #")
  print( "#                            buy me a drink:                              #")
  print( "#                   1PdGYTgZTTZgcJfKuokH8XoBgvqAntGUcA                    #")
  print( "###########################################################################")
  args         = get_args()
  exchange     = args.exchange
  seconds      = args.timeframe
  alert_volume = args.volume
  alert_type   = args.alert_type
  limit        = args.limit
  print( "\texchange: %s\ttimeframe: %s(s)\tvolume: %s BTC"%(exchange,
                                                seconds, alert_volume))
  # If audio_type
  if alert_type == "audio":
    print( "\talert: audio")
    audiofile    = args.audiofile
    print( "\taudiofile: %s"%(audiofile))
    player = find_player()
  elif "mail" in alert_type:
    print( "\talert: e-mail")
    host      = args.host
    port      = args.port
    sender    = args.sender
    recipient = args.recipient
    subject   = args.subject
    body      = args.body
    enc       = args.encryption
    print( "\thost:   %s port: %s encryption: %s"%(host, port, enc))
    print( "\tsender: %s recipient: %s"%(sender, recipient))
    print( "\tsubject: %s"%(subject))
  else:
    print( "[!] Alert %s not supported. Try: audio, e-mail"%alert_type)
    sys.exit(1)
  # main loop
  try:
    while(1):
      vol = calculate_vol( seconds)
      #print "[*] Vol: %s"%vol
      print("[*] Volume: "+str(vol), end="\r")
      if vol >= alert_volume:
        print( "[*] ALERT!", end="\r")
        # are we past last alert + limit?
        if last_alert + limit <= time.time():
          # our alert
          if alert_type == "audio":
            alert_audio( audiofile, player)
          elif "mail" in alert_type:
            alert_email( host, sender, recipient, subject, body, port, enc)
          # set last alert time (now!)
          last_alert = time.time()
        else:
          print( "[*] Alert rate-limited, skipping.", end="\r")
        time.sleep(1)
  except KeyboardInterrupt:
    print( "[*] Caught exit, quitting")
    sys.exit()
  except Exception as e:
    print( "[!] Error: %s"%e)
    sys.exit(1)
  print( "[*] Done.")
