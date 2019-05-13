# METAFONT examples

- Simple and easy metafont examples with TeX

## Compile sequence

1. Compile the whole font with the right parameters to get the 'gf' and 'tfm' files
2. Transform the 'gf' file into a 'pk' file
3. Move the 'pk' and 'tfm' files where they can be found by 'TeX'
4. Write a small 'TeX' file to check how your font looks like

- METAFONT is in 'proofing' mode by defaultwhich doesn't produce 'tfm'. 'gf' will have extension '.2602gf'.


## Sample code with steps

- ./mfmake.sh contains steps you can run on Mac

```
$ ./mfmake.sh beta B
```
