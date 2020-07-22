cd ../covid19/
git pull
cd ../Covid-19-IND/

cp ../covid19/data/mohfw.json data/mohfw.json

cat ../covid19/data/all_totals.json | grep cured | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/cured.csv

cat ../covid19/data/all_totals.json | grep death | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/deaths.csv

cat ../covid19/data/all_totals.json | grep total | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/confirmed.csv


echo "report_time,samples,individuals,confirmed_positive" > data/testing.csv

sed 1,1d ../covid19/data/icmr_testing_status.json | sed -r 's#\{[-"a-z:_|T0-9\.\+,]+\{[-"a-z:_|T0-9\.\+,]+report_time":"([-0-9T:\.\+]+)["a-z:,_]+([0-9]+|null)["a-z:,_]+([[0-9]+|null)["a-z:,_]+([0-9]+|null)["a-z:,_]+\}\},?#\1,\2,\3,\4#g' | sed -r 's#\]\}##g' | sed 's/null/nan/g'>> data/testing.csv
