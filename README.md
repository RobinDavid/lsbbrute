lsbbrute
========

Script to bruteforce the LSB of an image to find file signatures (in every channel permutation, rotation etc..)

This script has been written in order to facilitate the resolution of some CTF challenges by looking for file embbded in the LSB of an image.

How it works ?
==============

1. Bruteforce every channels (red, blue, green), and every channel combination (RGB, RBG, GRB, GBR, BGR, BRG).
2. For each image every rotation will be tested (0, 90, 180, 260)
3. On each of them either the LSB bit or the MSB bit will be tested
4. On each bits will be iterated line by line or column by column
5. Then the bits are joined together to form a string on which a file signature check is made. But also on the string reversed.

This makes a total of 288 possibilities on which every file signatures will be tested.

> A percentage of ascii characters is also computed for every tests in case plain text would be embbeded instead of a file.


Usage
=====

**lsbbrute.py** is meant to be used as script, but can also be used as a library along with ```filesig.py``` which is independent form ```lsbbrute.py```. You can try with an image sample taken from the NDH2k14 prequals CTF.

```bash
./lsbbrute.py imgs/GodMode.bmp
```

**Remarks**:

* By default when a match is found the embedded file is dump to a separate file. This can be modified by the class attribute ```save_match```
* The threshold for ascii character detection can also be modulated by the class attribute ```ascii_treshold```
* A list of signatures to ignore can also be used (see ```ignore_sigs``` attribute). This is especially useful to avoid false positive

