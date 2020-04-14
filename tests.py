from skimage import io as skimage_io

import csv
import picture_to_circuit as ptc
import ptc_debug

TESTS_FOLDER = "tests"
show_all = True

class TestRes:
	def __init__(self, test_name, given, expected):
		self.test_name = test_name
		self.given = given
		self.expected = expected
		
	def __str__(self):
		return f"{self.test_name}: given {self.given} - expected {self.expected}"
	
	def __repr__(self):
		return str(self)
	
	def failed(self):
		return self.given != self.expected

def run_test(params):
	
	tests = open(TESTS_FOLDER + "/test_data")
	tests = csv.DictReader(tests, delimiter="\t", quotechar="\"")

	test_results = {}
	
	for test in tests:
		img_file = test['img_file']
		print(f"converting {img_file}. | ", end = '')
		image = skimage_io.imread(TESTS_FOLDER + "/" + img_file)
		
		try:
			res = ptc.to_circuit(image, params)
			
			result = __evaluate(test, res)
			print(result)
			test_results[img_file] = result
		
			if any(t.failed() for t in result) or show_all:
				tracer = res['tracer']
				ptc_debug.plot_debug_info(res['tracer'])
		except Exception as err:
			print("Test failed with error: " + str(err))
		
	return test_results
	
def __evaluate(test, res):
	result = []
	
	#Number of circles:
	given, expected = (len(res['starts']), int(test['nbr_circles']))
	result.append(TestRes("nbr_circles", given, expected))
	
	return result

if __name__ == "__main__":
	params = ptc.default_params.copy()
	params['debug'] = True
	run_test(params)
	

