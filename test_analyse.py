from analyse import *
import json
import pytest

def test_date_comp():
	date_a = "1900-01-31"
	date_b = "2020-12-11"
	assert compare_date(date_a,date_b)
	assert compare_date(date_b,date_a) == False

def test_counter():
	testData = json.load(open("testdata.json")) 
	t_parser = parser()
	assert type(t_parser.__repr__()) == str
	t_parser.parse_hist(testData)
	sor_list = t_parser.get_sorted()
	assert sor_list[0][1]>sor_list[1][1]
	assert sor_list[0][0] == "peter"
	assert sor_list[0][1] == 2
	assert t_parser.hasParsed == True

def test_too_early_eval():
	t_parser = parser()
	assert t_parser.hasParsed == False
	with pytest.raises(RuntimeError):
		t_parser.export()
		t_parser.make_pie()

def test_parse_date():
	testData = json.load(open("testdata.json"))
	t_parser = parser()
	t_parser.parse_hist(testData)
	assert t_parser.maxDate == "2234-10-11 12:13:14 UTC"
	assert t_parser.minDate == "1900-10-11 12:13:14 UTC"
