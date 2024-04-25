from flask import Flask, request
import json


app = Flask(__name__)

fallback_search = '705e9d913c37b5f85ef56e7977d2a8b3c21bccd42e3431a91ed93def1b8adcf7'
fallback_dispensary = 'ad5003bb36e7f1392a88e3d03fb0ffa1abc3919299d514b8f1b40dcfce891af3'
fallback_product = '810d1b324c8eab049d0c0f781abb990f073867e3f88b900b85f99ac1a66e68ef'
fallback_details = 'c8bd105058480e1509522a02aaf241209b18e3f0ef5b1f360b1bef3554cb9392'
fallback_special = '285c44887684feb2d872407e339c74653abbc9ca1da9f5fa592e71fe26f2f121'


@app.route("/get",)
def get_hashes():
	main_hashes = {
		'DispensarySearchHash': fallback_search,
		'DispensaryHash': fallback_dispensary,
		'ProductHash': fallback_product,
		'ProductHashWithDetails': fallback_details,
		'SpecialHash': fallback_special
	}
	try:
		file = open('hashes.txt', 'r')
		hashes = json.load(file)
		file.close()
		if hashes['DispensarySearchHash'] and hashes['DispensaryHash'] and hashes['ProductHash'] and hashes["ProductHashWithDetails"] and hashes["SpecialHash"]:
			return hashes
		else:
			return main_hashes
	except:
		return main_hashes


@app.route("/save",)
def save_hashes():
	dispensary_search = request.args.get("DispensarySearchHash")
	dispensary_hash = request.args.get("DispensaryHash")
	product_hash = request.args.get("ProductHash")
	product_hash_details = request.args.get("ProductHashWithDetails")
	special_hash = request.args.get('SpecialHash')
	if not dispensary_search:
		dispensary_search = fallback_search
	if not dispensary_hash:
		dispensary_hash = fallback_dispensary
	if not product_hash:
		product_hash = fallback_product
	if not product_hash_details:
		product_hash_details = fallback_details
	if not special_hash:
		special_hash = fallback_special
	hashes = {
		'DispensarySearchHash': dispensary_search,
		'DispensaryHash': dispensary_hash,
		'ProductHash': product_hash,
		'ProductHashWithDetails': product_hash_details,
		'SpecialHash': special_hash
	}
	file = open('hashes.txt', 'w')
	file.write(json.dumps(hashes))
	file.close()
	return hashes


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1240)
