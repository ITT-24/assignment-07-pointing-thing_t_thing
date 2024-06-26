# 02 - Fitt's Law
Using the `config.csv`, you can change any parameter. That file will be used by default. Alternativly use: `py fitts-law.py -c path/to/config.csv`, for a custom file(path) (with the same format)

## Manual
- latency should be written in seconds (0.15 = 150 ms)

**The application logs:** (in `logs`-folder)
- [x] hit (True/False)
- [x] position of cursor on click 
- [x] position of clicked target
- [x] nicht distance für 2 clicks  (in 03) dann
- [x] time between appearance of new marked target and next click
- [x] parameters set in config (id, radius, distance, trial, ...)
- [x] latency hinzufügen
- [x] start screen hinzufügen



Fragen:
- Das File überschreibt sich immer > sollte eher immer ein neues erstellen oder mit terminal appenden lassen
- timestamp anstatt der direkt berechneten Zeit loggen ? Oder beides ?


## Task 3
Was wir wollen:

- [ ] graph mit geraden (scatter plot plus bias) und durchschnitt
- [ ] anzahl der Hit und Miss

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KHzC7ivQ)

