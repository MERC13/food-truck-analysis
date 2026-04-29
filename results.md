======================================================================
1) OPTIMAL Q-VALUES AND POLICY PER DAY
======================================================================

Day 1  |  Optimal policy: [3, 2, 1, 1, 3]  |  Data latent: [np.int64(3), np.int64(1), np.int64(1), np.int64(1), np.int64(3)]  |  V*(s1) = 96.82
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       81.15     77.85     58.35     41.85     10.67
  Park 2       85.01     78.15     57.45     28.98      7.71
  Park 3       96.82     63.35     50.52     34.75     22.25
  V*(h)      96.82     78.15     58.35     41.85     22.25

Day 2  |  Optimal policy: [3, 1, 1, 3, 3]  |  Data latent: [np.int64(3), np.int64(1), np.int64(1), np.int64(3), np.int64(3)]  |  V*(s1) = 85.51
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       67.75     65.18     48.18     30.23     11.29
  Park 2       73.89     61.01     48.10     22.16      7.67
  Park 3       85.51     53.01     40.00     32.43     16.43
  V*(h)      85.51     65.18     48.18     32.43     16.43

Day 3  |  Optimal policy: [3, 1, 2, 3, 1]  |  Data latent: [np.int64(3), np.int64(1), np.int64(1), np.int64(3), np.int64(1)]  |  V*(s1) = 89.44
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       69.85     67.28     41.40     27.17     16.00
  Park 2       73.13     62.52     41.77     23.11      8.50
  Park 3       89.44     46.92     36.40     29.40     13.29
  V*(h)      89.44     67.28     41.77     29.40     16.00

Day 4  |  Optimal policy: [3, 1, 1, 3, 3]  |  Data latent: [np.int64(3), np.int64(1), np.int64(1), np.int64(3), np.int64(3)]  |  V*(s1) = 100.08
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       79.82     77.25     58.75     37.00     10.57
  Park 2       84.68     73.75     55.25     31.70      8.29
  Park 3      100.08     63.44     48.11     41.25     23.00
  V*(h)     100.08     77.25     58.75     41.25     23.00

Day 5  |  Optimal policy: [3, 1, 2, 3, 1]  |  Data latent: [np.int64(3), np.int64(1), np.int64(2), np.int64(3), np.int64(1)]  |  V*(s1) = 100.96
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       82.51     79.79     52.67     35.17     18.67
  Park 2       88.36     73.46     60.29     25.67      6.43
  Park 3      100.96     67.46     46.42     40.17     10.43
  V*(h)     100.96     79.79     60.29     40.17     18.67

Day 6  |  Optimal policy: [3, 2, 2, 1, 3]  |  Data latent: [np.int64(3), np.int64(2), np.int64(2), np.int64(1), np.int64(3)]  |  V*(s1) = 98.42
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       83.07     76.79     56.00     41.75     10.00
  Park 2       86.78     79.92     63.12     27.67      6.29
  Park 3       98.42     69.79     48.25     37.50     21.50
  V*(h)      98.42     79.92     63.12     41.75     21.50

Day 7  |  Optimal policy: [3, 2, 2, 1, 3]  |  Data latent: [np.int64(3), np.int64(2), np.int64(2), np.int64(1), np.int64(3)]  |  V*(s1) = 89.26
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       76.28     71.96     49.30     38.50     13.43
  Park 2       79.00     73.42     56.62     26.17      6.86
  Park 3       89.26     62.12     45.21     35.00     19.50
  V*(h)      89.26     73.42     56.62     38.50     19.50

Day 8  |  Optimal policy: [3, 1, 2, 3, 3]  |  Data latent: [np.int64(3), np.int64(1), np.int64(2), np.int64(3), np.int64(3)]  |  V*(s1) = 113.62
              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1       95.79     92.79     62.07     38.93     16.50
  Park 2       97.93     87.29     67.29     31.50      6.12
  Park 3      113.62     72.29     55.52     49.67     22.33
  V*(h)     113.62     92.79     67.29     49.67     22.33

======================================================================
2) BASELINE HUMAN POLICY  π₀(park | hour)  [Days 1-2]
======================================================================

              Hour 1    Hour 2    Hour 3    Hour 4    Hour 5
  Park 1     0.509     0.205     0.259     0.268     0.393
  Park 2     0.259     0.527     0.277     0.482     0.304
  Park 3     0.232     0.268     0.464     0.250     0.304

  Inertia (P(stay at same park) | hours 2-5): 0.280
  Baseline latent-optimal match rate:          0.246
  Random baseline (1/3):                       0.333

======================================================================
3) COMPLIANCE ANALYSIS — RECOMMENDATIONS ONLY (Days 3-5)
======================================================================

3a. P(follow advice | advice shown) by frequency group
   10% group:  0.933  (n=15)
   50% group:  0.771  (n=144)
   90% group:  0.837  (n=251)

3b. P(follow advice | advice shown) by day
  Day 3,  10%:  1.000  (n=4)
  Day 3,  50%:  0.773  (n=44)
  Day 3,  90%:  0.857  (n=84)
  Day 4,  10%:  0.833  (n=6)
  Day 4,  50%:  0.755  (n=49)
  Day 4,  90%:  0.787  (n=80)
  Day 5,  10%:  1.000  (n=5)
  Day 5,  50%:  0.784  (n=51)
  Day 5,  90%:  0.862  (n=87)

3c. Latent compliance (chose optimal when advice NOT shown) by freq group
   10% group:  0.354  (n=240)
   50% group:  0.321  (n=156)
   90% group:  0.265  (n=34)

3d. Latent compliance by day (learning without seeing advice)
  Day 3:  0.264  (n=148)
  Day 4:  0.386  (n=145)
  Day 5:  0.358  (n=137)

3e. Compliance by hour (advice shown, days 3-5)
  Hour 1:  0.871  (n=85)
  Hour 2:  0.778  (n=72)
  Hour 3:  0.821  (n=78)
  Hour 4:  0.774  (n=84)
  Hour 5:  0.835  (n=91)

======================================================================
4) OPTIMAL RECOMMENDATION FREQUENCY (Days 3-5)
======================================================================

4a. Mean reward per round by frequency group
   10% group:  12.84
   50% group:  13.97
   90% group:  16.01

4b. Reward when advice IS shown vs NOT shown
   Group   w/ advice   w/o advice        Δ
     10%       16.53        12.61    +3.93
     50%       16.34        11.78    +4.56
     90%       16.73        10.71    +6.02

4c. Mean per-step shortfall  V*(h) - Q*(h, chosen_action)
   10% group:  mean shortfall = 5.864  (cumulative over 5h = 29.32)
   50% group:  mean shortfall = 4.558  (cumulative over 5h = 22.79)
   90% group:  mean shortfall = 2.253  (cumulative over 5h = 11.27)

4d. Latent-optimal rate across days (learning transfer)
   Day     10%     50%     90%
     1   0.141   0.210   0.137
     2   0.259   0.390   0.326
     3   0.247   0.304   0.182
     4   0.430   0.333   0.333
     5   0.388   0.327   0.250
     6   0.520   0.380   0.333
     7   0.545   0.462   0.333
     8   0.519   0.527   0.625

======================================================================
5) SOCIAL INFORMATION ANALYSIS (Days 6-8)
======================================================================

5a. P(follow advice | advice shown) by social condition x freq
             agree   against
     10%     1.000     1.000
     50%     0.785     0.897
     90%     0.774     0.926

5b. Latent compliance (no advice shown) by social condition x freq
             agree   against
     10%     0.524     0.533
     50%     0.306     0.639
     90%     0.273     0.533

5c. Mean reward per round by social condition x freq
             agree   against
     10%     16.07     15.85
     50%     13.70     16.62
     90%     16.76     18.22

5d. Compliance change: rec-only (days 3-5) → social (days 6-8)
           Rec only   + Social        Δ
     10%      0.933      1.000   +0.067
     50%      0.771      0.846   +0.075
     90%      0.837      0.853   +0.017

5e. Reward WITHOUT advice: rec-only vs social phase
           Rec only   + Social        Δ
     10%      12.61      15.51    +2.90
     50%      11.78      13.25    +1.47
     90%      10.71      12.96    +2.26

5f. Latent compliance by day in social phase, by condition
   Day     agree   against
     6     0.378     0.550
     7     0.391     0.609
     8     0.506     0.556