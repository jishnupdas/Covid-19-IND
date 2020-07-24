cd ../covid19/
git pull
cd ../Covid-19-IND/

#copy the data file
cp ../covid19/data/mohfw.json data/mohfw.json
cp ../covid19/data/all_totals.json data/all_totals.json

# grep keyword, match the line, use capture groups
grep cured ../covid19/data/all_totals.json | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/cured.csv

grep death ../covid19/data/all_totals.json | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/deaths.csv

grep total ../covid19/data/all_totals.json | sed -E 's#\{["a-z:]+\["([-0-9T:\.\+]+)[a-z",_]+\][a-z",_:]+([0-9]+)\},?#\1,\2#g' > data/confirmed.csv

#writing the heading to the file
echo "report_time,samples,individuals,confirmed_positive" > data/testing.csv

# skip first line, match the pattern, use capture groups, use (|) or conditions, remove last line, replace null with nan
sed 1,1d ../covid19/data/icmr_testing_status.json | sed -r 's#\{[-"a-z:_|T0-9\.\+,]+\{[-"a-z:_|T0-9\.\+,]+report_time":"([-0-9T:\.\+]+)["a-z:,_]+([0-9]+|null)["a-z:,_]+([[0-9]+|null)["a-z:,_]+([0-9]+|null)["a-z:,_]+\}\},?#\1,\2,\3,\4#g' | sed -r 's#\]\}##g' | sed 's/null/nan/g'>> data/testing.csv

# regex debug tool https://www.debuggex.com/
