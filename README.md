# 02 - Fitt's Law
Using the `config.csv`, you can change any parameter. That file will be used by default. Alternativly use: `py fitts-law.py -c path/to/config.csv`, for a custom file(path) (with the same format)

## Config Manual
- latency should be written in seconds (0.15 = 150 ms)
- repetitions is how many rounds of the experiment run
  - e.g. if you have 3 conditions (radii, distances), than those 3 conditions all run 3 times each
- device is the input device
  - used for saving the file
  - if you forget to change it, the program will not override files, but will ask you how to proceed (in the terminal) 

**The application logs:** (in `logs`-folder)
- [x] hit (True/False)
- [x] position of cursor on click 
- [x] position of clicked target
- [x] time between appearance of new marked target and next click
- [x] parameters set in config (id, radius, distance, trial, ...)
- [x] add latency 
- [x] add start screen
- [x] a timestamp of the when a the click occurs


## Task 3
Was wir wollen:

- [ ] graph mit geraden (scatter plot plus bias) und durchschnitt
- [ ] anzahl der Hit und Miss


## Probleme
- Lag hat am anfang nicht funktioniert
Am anfang hatten wir verzögerung ums doppelte und dann mit threading gelöst

- kamera boundary für task 1
ende der kamera war nicht ende des bildschirms (Rand) -> haben padding eingebau und von klein auf groß umgerechnet 

- Falls ein Klick-Event ausgeführt werden sollte, wurden immer ganz viele ausgelöst
Am Ende einen einfachen Check eingeführt, bei dem man erst "loslassen" muss, bevor ein neuer Event triggern kann



[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KHzC7ivQ)

