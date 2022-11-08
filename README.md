# PicoGopher

PicoGopher is a Gopher server tiny enough to run on a Raspberry Pi Pico W.

## Why Gopher?

As a protocol, Gopher has been around since 1991. 
It is best suited for sharing information in the form of plain text 
and for this reason it **focuses on content** much more than presentation. 
It is very **simple**, so one can implement a server in a few lines of code.
It is very **light**, so it can run on small, cheap devices without breaking 
a sweat (which also means with a **very low power consumption**).

Using Gopher is also a stance. 
In a period when the default way to read and share contents goes through some 
large social networks, choosing to use it is a mindful choice which also 
provides some advantages: for instance, no tracking / sharing of personal 
information, no ads, no recommendation algorithms trying to keep you longer 
on a platform, just a (relatively small) community of real people sharing 
their thoughts.

## Should I fully embrace Gopher and leave everything else?

Hell no :-) 
Gopher is not for everyone. I mean, technically yes: just install a Gopher 
browser and you are ready to explore it! But still, you might just realise 
you prefer other types of media/contents/topics. That's perfectly ok!

Also, Gopher is not the only alternative to social networks. It is just one 
of the many facets of the "Small Internet" movement, which is delightfully 
described in James Tomasino's talk 
[Rocking the Web Bloat: Modern Gopher, Gemini and the Small Internet](https://media.ccc.de/v/mch2022-83-rocking-the-web-bloat-modern-gopher-gemini-and-the-small-internet). 
[Gemini](https://gemini.circumlunar.space/), for instance, is another, more 
recent, super interesting protocol and another completely new world to learn
more about.

## Will there be a PicoGemini?

Most likely yes... Especially if you don't expect me to be the one who 
codes it :-) 


# Running the code

PicoGopher's code is in an early stage... But it already works (yay!). To
run it:

- make sure you have [micropython](https://micropython.org/download/rp2-pico-w/)
flashed onto your Pico
- add your gopherhole to the `/gopher` folder on the Pico (e.g. using
  [Thonny](https://thonny.org/)'s file manager)
- copy the four python files in the root folder on the Pico
- connect the Pico to a power source: it will automatically start running
  the code in `main.py`.

When started, PicoGopher creates a new open WiFi AP with essid `JOIN ¯\_(ツ)_/¯ ME`.
After joining the AP, one can browse your gopherhole contents by connecting
to [gopher://192.168.4.1](gopher://192.168.4.1).


# Creating PicoGopher

I am trying to document the steps that brought me to zero to pico (yeah they 
are very tiny ones...). In the `/phlog` folder you can find the code I refer
to in the first three posts I wrote.

Of course everything I wrote is published on Gopher :-). You can find it at
[gopher://gopher.3564020356.org](gopher://gopher.3564020356.org) (if you do not have
a Gopher browser you can connect [here](https://gopher.floodgap.com/gopher/gw?a=gopher%3A%2F%2Fgopher.3564020356.org)).



