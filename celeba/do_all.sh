for i in 0.0 0.1 0.2 0.3 0.4 0.6 0.7 0.8 0.9 1.0
do
python perf_quart.py --filter Male --ratio_1 0.5 --ratio_2 $i
python perf_quart.py --filter Young --task Male --ratio_1 0.5 --ratio_2 $i
done