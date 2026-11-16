# Hormones, brain and movement: tests on public data

Sex hormones change across the menstrual cycle, with hormonal contraception and at menopause, and they act on both the brain and the motor system. Open datasets that record movement rarely record any of this: CAPTURE-24 gives only sex and age, and NHANES measures estradiol once but not the day of the cycle. Studies that do consider the cycle usually place their sessions by counting days.

This repository uses four public datasets to test what such designs can and cannot detect: how often a counted cycle day falls in the intended phase, how large a hormonal difference in resting EEG must be to be seen in a typical sample, whether a wrist activity classifier depends on the sex of the people it was trained on, and how daily activity relates to menopause and to a single estradiol value.

## Key results

| Figure | Data | Question | Result |
|---|---|---|---|
| [1](Findings/Figure1.md) | Marquette cycle data: 1498 cycles of 157 women | How often does a counted cycle day fall in the intended phase? | Ovulation fell on day 14 in 15% of cycles (median day 15, IQR 14 to 18), and moved between cycles of the same woman with an SD of 2.2 days. A session on day 21 fell in the mid-luteal window (5 to 9 days after the estimated ovulation) in 60% of cycles; counting back from the woman's usual cycle length, in 66%; from the actual next menstruation, known only afterwards, in 77%. |
| [2](Findings/Figure2.md) | OpenNeuro ds007615: resting EEG of 69 women | Does resting EEG differ with hormonal contraception or self-reported phase, and what could this sample detect? | No measure differed between 37 contraceptive users and 32 non-users after correction for seven measures; the largest difference was in absolute alpha power (0.48 SD, 95% CI −0.00 to 0.96). With 80% power the sample could detect 0.69 SD between users and non-users, and 1.13 SD between luteal and other non-users. The dataset's phase label follows fixed cycle days; counting back from the usual cycle length gave the same phase for 14 of 26 non-users. |
| [3](Findings/Figure3.md) | CAPTURE-24: 24 h wrist accelerometry of 99 women and 52 men | Does an activity classifier work better for people of the sex it was trained on? | Barely. Macro F1 was 0.67 to 0.68 for every training set and test sex. Training on the participant's own sex changed macro F1 by +0.004 for women (95% CI −0.003 to 0.011) and −0.000 for men (−0.012 to 0.010), against an SD of 0.088 between people. The one clear class effect was light activity in women (+0.015 F1, 95% CI 0.008 to 0.022). |
| [4](Findings/Figure4.md) | NHANES 2013–2014: wrist accelerometry of 3815 adults | Do daily activity and sleep differ with sex, menopause and estradiol? | Women recorded more wrist activity than men (+0.80 thousand MIMS units a day, age-adjusted, 95% CI 0.55 to 1.05). At 40 to 59, women after menopause did not differ clearly from women who still menstruated (activity −0.07 SD, 95% CI −0.46 to 0.32). In 679 menstruating women estradiol spanned 11 to 283 pg/mL (5th to 95th percentile) and was not associated with daily activity (0.03 SD per doubling, 95% CI −0.03 to 0.09). |

## What the four analyses show together

**Counting days misplaces a large share of sessions.** Even with the actual cycle length, almost a quarter of planned mid-luteal sessions fell outside the window, and the prospective rules missed a third or more. If a session that misses the window carries no luteal effect, the expected difference shrinks by the hit rate and the number of women needed grows by 1.7 to 2.8 times (Figure 1). The EEG data show the same problem from the other side: the phase label of 12 of 26 women changed with the counting rule (Figure 2).

**A single session per woman detects only large effects.** Comparing 37 with 32 women, the EEG sample could detect 0.69 SD; a difference of 0.5 SD between two groups needs about 64 women per group. Recording the same women in two phases would need about 15 women for 0.5 SD if the measure is stable between sessions (correlation 0.8, assumed rather than measured here). Combined with Figure 1, this points to within-woman designs with sessions scheduled from a detected LH surge or checked with a hormone measurement.

**For four coarse activity classes, the sex of the training participants hardly matters.** Whether finer measures of movement, such as gait, balance or force control, change with sex or with the cycle cannot be tested with these datasets.

**A hormone value without the cycle day mixes person and phase.** In NHANES, estradiol in menstruating women varied 25-fold and was not related to daily activity or sleep. The spread is expected from the cycle itself, and a survey that does not record the cycle day cannot separate the two.

## Data

| Dataset | Used here | Licence | Source |
|---|---|---|---|
| Marquette menstrual cycle data (Fehring 2012) | Cycle length, estimated day of ovulation, luteal length | Released by Marquette University for reuse; no licence named | [epublications.marquette.edu/data_nfp/7](https://epublications.marquette.edu/data_nfp/7) |
| OpenNeuro ds007615 (Normannseth, Andersson and Hatlestad-Hall) | Resting EEG, eyes closed and open; contraception and cycle questionnaire | CC0 | [doi:10.18112/openneuro.ds007615.v1.0.0](https://doi.org/10.18112/openneuro.ds007615.v1.0.0) |
| CAPTURE-24 (Chan et al. 2024) | Wrist accelerometry with activity labels, sex and age band | CC BY 4.0 | [Oxford Research Archive](https://ora.ox.ac.uk/objects/uuid:99d7c092-d865-4a19-b096-cc16440cd001) |
| NHANES 2013–2014 (US National Center for Health Statistics) | Wrist accelerometer day summaries, serum estradiol, reproductive health, prescriptions, body measures | Public domain | [wwwn.cdc.gov/nchs/nhanes](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013) |

No data are stored in this repository. The code is released under the MIT licence.

## Running the analyses

```
pip install -r requirements.txt
python download_cycle_data.py          # about 26 GB; the Marquette file is saved by hand (the script says where)
jupyter notebook
```

Run each notebook from the repository folder. Data are read from `data/` by default; the environment variables `MARQUETTE`, `DS007615`, `CAPTURE24` and `NHANES` point the notebooks elsewhere.

| Notebook | Figure | First run on a two-core laptop |
|---|---|---|
| [cycle_day_counting.ipynb](cycle_day_counting.ipynb) | 1 | seconds |
| [eeg_contraception_phase.ipynb](eeg_contraception_phase.ipynb) | 2 | about 5 minutes (spectra of 138 recordings, then cached) |
| [activity_training_sex.ipynb](activity_training_sex.ipynb) | 3 | about 35 minutes (features of 151 participants and 50 splits, then cached) |
| [nhanes_activity_hormones.ipynb](nhanes_activity_hormones.ipynb) | 4 | seconds |

Each notebook writes its figure to `figures/` and its numbers to `results/`.

## Repository layout

```
├── README.md
├── Limitations.md
├── LICENSE
├── Findings/                  one page per figure: methods, numbers and interpretation
├── *.ipynb                    one notebook per figure
├── figures/
├── results/                   numbers behind each figure (JSON)
├── download_cycle_data.py
└── requirements.txt
```

See [Limitations.md](Limitations.md) for what these analyses cannot show.
