virtualcurrency trading alerts
==============================

A simple alert system for when volume on a Bitcoin Exchange hits a certain number in a specified timeframe. When volume hits a certain threshold, you can be alerted in two ways: through an audio file being played or via e-mail. Hopefully you'll hear it, in the inevitable middle of the night, wake up, and profit (or panic).

Helpful? Leave a tip: `1PdGYTgZTTZgcJfKuokH8XoBgvqAntGUcA`

OSX and Windows binaries are also available by request (and donation!): brandon ..at_ bxroberts  .dot. org

## USAGE

    usage: trade_alert.py [-h] [--limit LIMIT] [--audiofile AUDIOFILE]
                               [--host HOST] [--port PORT] [--sender SENDER]
                               [--recipient RECIPIENT] [--subject SUBJECT]
                               [--body BODY] [--encryption ENCRYPTION]
                               exchange timeframe volume alert_type

    Play an audio or send an e-mail alert when trade volume in the past number of
    seconds reaches a specified amount.

    positional arguments:
      exchange              Which exchange to monitor: gox
      timeframe             Timeframe to look back in seconds
      volume                Volume threshold to alert above
      alert_type            Type of alert: audio, e-mail

    optional arguments:
      -h, --help            show this help message and exit
      --limit LIMIT         Wait this number of seconds between alerts. Default:
                            300
      --audiofile AUDIOFILE
                            Location of audio file to play. Default: notify.wav
      --host HOST           SMTP host
      --port PORT           SMTP port
      --sender SENDER       E-mail alert sender
      --recipient RECIPIENT
                            E-mail alert recipient
      --subject SUBJECT     E-mail alert subject
      --body BODY           E-mail alert body
      --encryption ENCRYPTION
                            SMTP server encryption: tls, ssl, none
## E-Mail Alert

Example e-mail alert with 5-minute volume on Mt. Gox hits 500BTC:

`./trade_alert.py gox 300 500 e-mail --host mydomain.org --port 587 --recipient me@mydomain.org --sender me@mydomain.org`

SSL, TLS, and plain SMTP (no encryption) is supported with the `--encryption` option. Also pay attention to the `--limit` option. It's currently set to 300 seconds, but you may want to set it higher so you don't nuke your inbox.

## Audio Alert

Example of an audio alert for 500BTC volume in last 5 mins:

`./trade_alert.py gox 300 500 audio --audiofile ./notify.wav`

Audio is played using command line tools. Currently tools are tried in the following order:

### Linux

1. aplay
2. /dev/dsp
3. vlc

### Windows

1. vlc

### OSX

1. vlc

I'll also accept pull requests for more players/platforms.
