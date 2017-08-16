# stat_collector

Parse specific log files with events sequences.

(Input data example into example folder) 


1. Clone repo

2. Create virtualenv and install requirements
```textmate
$ virtualenv -p python2.7 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

3.Run tests
```textmate
✗ nosetests -v
test_get_max_response_times_list (test_get_max_response_times.TestGetMaxResponseTime) ... ok
test_my_percentile_is_equal_to_numpy_percentile (test_percentile.TestPercentile) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.048s

OK

```

3. Try to run on real data.

```textmate

bin/python log_stat.py --h
usage: log_stat.py [-h] input_file output_file

Parse log file into statistic file.

positional arguments:
  input_file   Filename to read from and parse.
  output_file  Filename to write result.

optional arguments:
  -h, --help   show this help message and exit

```

```textmate
 ✗ python log_stat.py example/1.in example/1.out
```

Output results into example/1.out
