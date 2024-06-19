# _*_ coding: utf-8 _*_

from flask import Flask, jsonify, render_template, request, make_response
import cv2
import base64
import numpy as np

app = Flask(__name__)


@app.route('/')
def index():
  return render_template("index.html")

@app.route('/test1', methods=['GET', 'POST'])
def rest_api_test1():
  print(request.method)
  data = {"0": "0.01", "1": "0.99"}
  if request.method == 'GET':
    param = request.args.get('data')
    print(param)
    data.update({"param": param})
  elif request.method == 'POST':
    param = request.form.get('data')
    print(param)
    f = request.files['file']
    print(f.filename)
    f.save(f.filename)
    data.update({"param": param, "file": f.filename})
  #return jsonify(data)
  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

@app.route('/test2', methods=['GET', 'POST'])
def rest_api_test2():
  print(request.method)
  data = {"0": "0.01", "1": "0.99"}
  if request.method == 'GET':
    param = request.args.get('data')
    print(param)
    data.update({"param": param})
  elif request.method == 'POST':
    param = request.form.get('data')
    print(param)
    f = request.files['file']
    print(f.filename)
    f.save(f.filename)
    data.update({"param": param, "file": f.filename})

  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response


#@app.route('/test_img', methods=['POST'])
@app.route('/analyze_img', methods=['POST'])
def rest_img_test():
  param = request.form.get('data')
  print(param)
  f = request.files['file']
  filestr = f.read()
  # FileStorage의 이미지를 넘파이 배열로 만듬
  npimg = np.frombuffer(filestr, np.uint8)
  # 넘파일 배열을 이미지 배열로 변환함
  img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
  # 여기에서 처리를 하면 됨
  #img_out = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#  img_canny = cv2.Canny(img_out, 50, 200)
  cv2.imwrite(f.filename, img)
  # cv2.imwrite(f.filename, img_out)
  #img_str = base64.b64encode(cv2.imencode('.jpg', img_out)[1]).decode()
  img_str = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
  data = {"param": param, "file": img_str}
  response = make_response(jsonify(data))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response


if __name__ == '__main__':
  app.debug = False
  #app.run(host="127.0.0.1", port="5000")
  app.run(host="0.0.0.0", port="5000")